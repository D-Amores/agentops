from pathlib import Path
from typing import Any, Protocol
from uuid import UUID

from langchain_core.tools import BaseTool
from langchain_deepseek import ChatDeepSeek
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import SecretStr

from app.agents.rag_tool import build_search_documents_tool
from app.agents.state import AgentState
from app.agents.tools import get_current_datetime
from app.core.config import get_settings
from app.repositories.document_chunk_repository import DocumentChunkRepositoryProtocol

settings = get_settings()

_WEATHER_SERVER_PATH = Path(__file__).parent.parent.parent / "mcp_servers" / "weather_server.py"

MCP_CLIENT = MultiServerMCPClient(
    {
        "weather": {
            "command": "python",
            "args": [str(_WEATHER_SERVER_PATH)],
            "transport": "stdio",
        }
    }
)


class _ModelNode(Protocol):
    async def __call__(self, state: AgentState) -> dict[str, Any]: ...


async def _build_call_model_node(
    model: str, owner_id: UUID, chunk_repository: DocumentChunkRepositoryProtocol
) -> tuple[_ModelNode, list[BaseTool]]:
    mcp_tools = await MCP_CLIENT.get_tools()
    rag_tools = build_search_documents_tool(owner_id, chunk_repository)
    all_tools = [get_current_datetime, rag_tools, *mcp_tools]

    llm = ChatDeepSeek(model=model, api_key=SecretStr(settings.DEEPSEEK_API_KEY), temperature=0)
    llm_with_tools = llm.bind_tools(all_tools)

    async def call_model(state: AgentState) -> dict[str, Any]:
        response = await llm_with_tools.ainvoke(state["messages"])
        return {"messages": [response]}

    return call_model, all_tools


async def build_agent_graph(
    model: str, owner_id: UUID, chunk_repository: DocumentChunkRepositoryProtocol
) -> CompiledStateGraph[AgentState, None, AgentState, AgentState]:
    call_model_node, all_tools = await _build_call_model_node(model, owner_id, chunk_repository)

    graph = StateGraph(AgentState)

    graph.add_node("agent", call_model_node)
    graph.add_node("tools", ToolNode(all_tools))

    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")

    return graph.compile()

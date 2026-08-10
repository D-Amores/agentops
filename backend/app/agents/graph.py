from pathlib import Path
from typing import Any, Protocol

from langchain_core.tools import BaseTool
from langchain_deepseek import ChatDeepSeek
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import SecretStr

from app.agents.state import AgentState
from app.agents.tools import get_current_datetime
from app.core.config import get_settings

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


async def _build_call_model_node(model: str) -> tuple[_ModelNode, list[BaseTool]]:
    mcp_tools = await MCP_CLIENT.get_tools()
    all_tools = [get_current_datetime, *mcp_tools]

    llm = ChatDeepSeek(model=model, api_key=SecretStr(settings.DEEPSEEK_API_KEY), temperature=0)
    llm_with_tools = llm.bind_tools(all_tools)

    async def call_model(state: AgentState) -> dict[str, Any]:
        response = await llm_with_tools.ainvoke(state["messages"])
        return {"messages": [response]}

    return call_model, all_tools


async def build_agent_graph(
    model: str,
) -> CompiledStateGraph[AgentState, None, AgentState, AgentState]:
    call_model_node, all_tools = await _build_call_model_node(model)

    graph = StateGraph(AgentState)

    graph.add_node("agent", call_model_node)
    graph.add_node("tools", ToolNode(all_tools))

    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")

    return graph.compile()

from typing import Any, Protocol

from langchain_deepseek import ChatDeepSeek
from langgraph.graph import START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import SecretStr

from app.agents.state import AgentState
from app.agents.tools import get_current_datetime
from app.core.config import get_settings

settings = get_settings()
AVAILABLE_TOOLS = [get_current_datetime]


class _ModelNode(Protocol):
    async def __call__(self, state: AgentState) -> dict[str, Any]: ...


def _build_call_model_node(model: str) -> _ModelNode:
    llm = ChatDeepSeek(model=model, api_key=SecretStr(settings.DEEPSEEK_API_KEY), temperature=0)
    llm_with_tools = llm.bind_tools(AVAILABLE_TOOLS)

    async def call_model(state: AgentState) -> dict[str, Any]:
        response = await llm_with_tools.ainvoke(state["messages"])
        return {"messages": [response]}

    return call_model


def build_agent_graph(
    model: str,
) -> CompiledStateGraph[AgentState, None, AgentState, AgentState]:
    graph = StateGraph(AgentState)

    graph.add_node("agent", _build_call_model_node(model))
    graph.add_node("tools", ToolNode(AVAILABLE_TOOLS))

    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")

    return graph.compile()

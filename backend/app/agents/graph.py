from typing import Any, Protocol

from langchain_deepseek import ChatDeepSeek
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from pydantic import SecretStr

from app.agents.state import AgentState
from app.core.config import get_settings

settings = get_settings()


class _ModelNode(Protocol):
    async def __call__(self, state: AgentState) -> dict[str, Any]: ...


def _build_call_model_node(model: str) -> _ModelNode:
    llm = ChatDeepSeek(model=model, api_key=SecretStr(settings.DEEPSEEK_API_KEY), temperature=0)

    async def call_model(state: AgentState) -> dict[str, Any]:
        response = await llm.ainvoke(state["messages"])
        return {"messages": [response]}

    return call_model


def build_agent_graph(
    model: str,
) -> CompiledStateGraph[AgentState, None, AgentState, AgentState]:
    graph = StateGraph(AgentState)

    graph.add_node("agent", _build_call_model_node(model))
    graph.add_edge(START, "agent")
    graph.add_edge("agent", END)

    return graph.compile()

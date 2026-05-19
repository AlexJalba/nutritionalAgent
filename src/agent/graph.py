"""LangGraph StateGraph for the Nutrition Advisor Agent."""
import os
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from src.agent.state import AgentState
from src.agent.prompts import SYSTEM_PROMPT
from src.tools.nutrition_lookup import nutrition_lookup
from src.tools.calorie_calculator import calorie_calculator
from src.tools.bmi_bmr import bmi_bmr_calculator
from src.tools.macro_tracker import log_food, get_daily_summary
from src.tools.meal_plan_generator import generate_meal_plan

TOOLS = [
    nutrition_lookup,
    calorie_calculator,
    bmi_bmr_calculator,
    log_food,
    get_daily_summary,
    generate_meal_plan,
]

_MAX_ITERATIONS = 10


def build_graph(model: str = "claude-sonnet-4-6") -> StateGraph:
    """Build and compile the nutrition advisor LangGraph."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY environment variable is not set.")

    llm = ChatAnthropic(model=model, max_tokens=4096, anthropic_api_key=api_key)
    llm_with_tools = llm.bind_tools(TOOLS)

    tool_node = ToolNode(TOOLS)

    def call_llm(state: AgentState) -> dict:
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def should_continue(state: AgentState) -> str:
        last_message = state["messages"][-1]
        # Count tool call iterations to enforce max_iterations guard
        tool_call_count = sum(
            1 for m in state["messages"] if hasattr(m, "tool_calls") and m.tool_calls
        )
        if tool_call_count >= _MAX_ITERATIONS:
            return END
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END

    graph_builder = StateGraph(AgentState)
    graph_builder.add_node("llm", call_llm)
    graph_builder.add_node("tools", tool_node)
    graph_builder.set_entry_point("llm")
    graph_builder.add_conditional_edges("llm", should_continue, {"tools": "tools", END: END})
    graph_builder.add_edge("tools", "llm")

    return graph_builder.compile()


# Module-level compiled graph (lazy — instantiated on first import of get_graph())
_graph = None


def get_graph() -> StateGraph:
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph

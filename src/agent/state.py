"""AgentState definition for the Nutrition Advisor LangGraph."""
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    user_profile: dict   # height, weight, age, gender, goal, restrictions
    daily_log: dict      # running calorie/macro totals for the session

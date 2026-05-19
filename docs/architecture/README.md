# Architecture — Nutritional Agent

## Overview

The agent is a stateful conversational loop built on **LangGraph** (`StateGraph`). Each user message enters the graph, the LLM decides whether to call a tool or respond directly, and the result is returned to the user. State (conversation history) is carried forward across turns within a session.

```
User input
    │
    ▼
validate_input()          ← length cap + injection pattern filter
    │
    ▼
LangGraph StateGraph
    │
    ├─► llm node          ← ChatAnthropic + bound tools
    │       │
    │       ├─ tool_calls present? ──► tools node (ToolNode)
    │       │                              │
    │       │                              └──► back to llm node
    │       │
    │       └─ no tool calls / max_iterations reached ──► END
    │
    ▼
Agent response → printed to user
```

---

## Components

### `src/agent/graph.py` — StateGraph

Builds and compiles the LangGraph graph.

- **`build_graph(model)`** — instantiates `ChatAnthropic`, binds all tools via `llm.bind_tools(TOOLS)`, wires up nodes and edges, and compiles.
- **`call_llm(state)`** — node function: prepends the system prompt to messages, invokes the LLM, appends the response to state.
- **`should_continue(state)`** — conditional edge: routes to `tools` if the last message has tool calls and `max_iterations` (10) has not been reached; otherwise routes to `END`.
- **`get_graph()`** — lazy singleton accessor used by `main.py`.

### `src/agent/state.py` — AgentState

```python
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]  # full conversation history
    user_profile: dict                        # age, weight, height, goal, restrictions
    daily_log: dict                           # running macro totals
```

`add_messages` is a LangGraph reducer — it appends new messages to the list rather than replacing it.

### `src/agent/prompts.py` — System Prompt & Input Validation

- **`SYSTEM_PROMPT`** — constrains the agent to nutrition advice, forbids meta-instructions from users, and lists available tools.
- **`validate_input(user_input)`** — returns `(is_valid, error_message)`. Rejects empty input, input over 2000 characters, and strings matching any of 6 compiled injection patterns.

### `src/tools/` — Tool Definitions

All tools are decorated with `@tool` from `langchain_core.tools`, which auto-generates the JSON schema LangChain passes to Claude.

| File | Tool(s) | External I/O |
|---|---|---|
| `nutrition_lookup.py` | `nutrition_lookup` | USDA FoodData Central API (HTTPS) |
| `calorie_calculator.py` | `calorie_calculator` | None (local equation) |
| `bmi_bmr.py` | `bmi_bmr_calculator` | None (local equation) |
| `macro_tracker.py` | `log_food`, `get_daily_summary` | None (in-memory dict) |
| `meal_plan_generator.py` | `generate_meal_plan` | None (string template) |

Each tool validates its own inputs and returns a human-readable string on both success and error — Claude incorporates error strings into its reasoning rather than crashing the loop.

### `src/models/nutrition.py` — Pydantic Models

Defines `NutritionInfo`, `UserProfile`, and `DailyLog` as `BaseModel` subclasses with field-level validation. Used for type safety within tools and as documentation for expected data shapes.

### `main.py` — CLI Entry Point

1. Loads `.env` and fails fast if `ANTHROPIC_API_KEY` is missing or is the placeholder value.
2. Initialises `AgentState` with empty messages, profile, and log.
3. Runs a `while True` input loop: validates input → appends `HumanMessage` → invokes graph → prints last message.

---

## Data Flow — Example: "How many calories in 100g of chicken breast?"

```
1. main.py         validate_input("How many calories in 100g of chicken breast?")  → valid
2. main.py         state["messages"].append(HumanMessage(...))
3. graph.py        call_llm(state)
                     → ChatAnthropic sees system prompt + user message
                     → returns AIMessage with tool_call: nutrition_lookup("chicken breast")
4. graph.py        should_continue → "tools"
5. ToolNode        nutrition_lookup.invoke({"food_query": "chicken breast"})
                     → GET https://api.nal.usda.gov/fdc/v1/foods/search?query=chicken+breast
                     → returns "Chicken, broilers ... 165 kcal, protein 31g ..."
6. graph.py        call_llm(state)  ← now includes ToolMessage with nutrition data
                     → ChatAnthropic synthesises answer
                     → returns AIMessage (no tool calls)
7. graph.py        should_continue → END
8. main.py         print(last_message.content)
```

---

## Security Design

| Concern | Mitigation |
|---|---|
| API key exposure | Loaded from `.env` only; fail-fast on missing/placeholder key; `.gitignore` covers `.env*` |
| Prompt injection | `validate_input()` screens for 6 injection patterns before LLM sees the input |
| Scope creep | System prompt hard-constrains agent to nutrition topics |
| Runaway tool loops | `max_iterations=10` cap in `should_continue` |
| Tool input abuse | Each tool validates its own parameters and returns error strings on invalid input |
| PII logging | No user health data written to disk in current implementation |

---

## Extending the Agent

### Add a new tool

1. Create `src/tools/my_tool.py` with a `@tool`-decorated function.
2. Import it in `src/agent/graph.py` and add it to the `TOOLS` list.
3. Add unit tests in `tests/test_tools.py`.

### Enable session persistence (SQLite checkpointing)

Uncomment and wire up `SqliteSaver` in `graph.py`:

```python
from langgraph.checkpoint.sqlite import SqliteSaver

memory = SqliteSaver.from_conn_string("nutrition_advisor.db")
graph = graph_builder.compile(checkpointer=memory)
```

Pass a `thread_id` in the config when invoking:

```python
graph.invoke(state, config={"configurable": {"thread_id": "user-123"}})
```

### Switch LLM model

```python
# In main.py or graph.py
graph = build_graph(model="claude-opus-4-7")
```

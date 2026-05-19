# Nutritional Agent

A conversational nutrition advisor built with [LangChain](https://python.langchain.com/) and [LangGraph](https://langchain-ai.github.io/langgraph/), powered by Anthropic Claude. Ask questions about food, track your daily macros, calculate calorie needs, and get meal plan suggestions — all through a natural language CLI.

---

## Features

| Capability | Description |
|---|---|
| Nutrition lookup | Real-time food data from the USDA FoodData Central API |
| Calorie / TDEE calculator | Daily energy needs via Mifflin-St Jeor equation |
| BMI & BMR calculator | Body mass index and basal metabolic rate |
| Macro tracker | Log meals and track daily calorie/macro totals |
| Meal plan generator | Personalized meal templates based on calorie targets and dietary restrictions |
| Injection-safe input | Validates and sanitises all user input before it reaches the LLM |
| Stateful conversation | Full message history maintained across turns in a single session |

---

## Requirements

- Python 3.10+
- An [Anthropic API key](https://console.anthropic.com/)

---

## Quick Start

```bash
# Clone the repo
git clone https://github.com/AlexJalba/nutritionalAgent.git
cd nutritionalAgent

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure your API key
cp .env.example .env
# Open .env and set:  ANTHROPIC_API_KEY=sk-ant-...

# Run the agent
python main.py
```

---

## Example Session

```
============================================================
  Nutrition Advisor Agent
  Powered by LangChain + Claude
  Type 'quit' or 'exit' to stop.
============================================================

You: How many calories are in 100g of chicken breast?
Agent: Chicken breast contains approximately 165 kcal per 100g —
       31g protein, 0g carbs, 3.6g fat.

You: Calculate my TDEE. I'm 30, male, 75kg, 178cm, moderately active.
Agent: BMR: 1,776 kcal/day | TDEE (moderate): 2,753 kcal/day |
       Recommended to maintain weight: 2,753 kcal/day.

You: What's my BMI?
Agent: BMI: 23.7 — Normal weight. BMR: 1,776 kcal/day.

You: Log that I ate a banana — 89 kcal, 1g protein, 23g carbs, 0.3g fat.
Agent: Logged 'banana'. Daily totals: 89 kcal | protein 1.0g | carbs 23.0g | fat 0.3g.

You: Give me a 3-meal plan for 2000 kcal, goal: lose weight, vegan.
Agent: Here's a vegan 2000 kcal/day meal plan for weight loss: ...

You: quit
Goodbye! Stay healthy.
```

---

## Project Structure

```
nutritionalAgent/
├── main.py                        # CLI entry point
├── requirements.txt
├── .env.example                   # API key template
├── src/
│   ├── agent/
│   │   ├── graph.py               # LangGraph StateGraph definition
│   │   ├── state.py               # AgentState TypedDict
│   │   └── prompts.py             # System prompt + input validation
│   ├── tools/
│   │   ├── nutrition_lookup.py    # USDA FoodData Central API
│   │   ├── calorie_calculator.py  # TDEE via Mifflin-St Jeor
│   │   ├── bmi_bmr.py             # BMI and BMR calculator
│   │   ├── macro_tracker.py       # Daily food log
│   │   └── meal_plan_generator.py # Meal plan template builder
│   ├── models/
│   │   └── nutrition.py           # Pydantic data models
│   └── memory/
│       └── __init__.py            # Reserved for future persistence layer
└── tests/
    ├── test_tools.py              # Tool unit tests (20 tests)
    └── test_agent.py              # Agent graph unit tests (6 tests)
```

---

## Running Tests

```bash
pytest tests/ -v
# Expected: 26 passed
```

With coverage:

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

---

## Configuration

| Environment variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic API key |

The agent uses `claude-sonnet-4-6` by default. To switch models, edit `src/agent/graph.py`:

```python
graph = build_graph(model="claude-opus-4-7")
```

---

## Security Notes

- The API key is loaded from `.env` only — never hardcoded. The app exits immediately if the key is missing.
- All user input is validated for length (max 2000 chars) and screened for prompt injection patterns before reaching the LLM.
- A strict system prompt limits the agent to nutrition topics only.
- The agent loop is capped at 10 tool-call iterations to prevent runaway execution.

---

## License

MIT

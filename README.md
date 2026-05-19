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

## Deployment on AWS

### Option A — EC2 (CLI)

The simplest deployment: run the CLI directly on an EC2 instance.

**1. Launch an EC2 instance**
- AMI: Amazon Linux 2023 or Ubuntu 22.04
- Instance type: `t3.micro` (free tier eligible)
- Security group: allow SSH (port 22) from your IP only

**2. Connect and set up**
```bash
ssh -i your-key.pem ec2-user@<your-ec2-ip>

# Amazon Linux 2023
sudo dnf install -y python3.11 python3.11-pip git

# Ubuntu
# sudo apt install -y python3.11 python3.11-venv git

git clone https://github.com/AlexJalba/nutritionalAgent.git
cd nutritionalAgent

python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
python main.py
```

---

### Option B — EC2 + FastAPI (HTTP API)

Expose the agent as an HTTP endpoint so it can be called from any client.

**1. Add `api.py` to the project root:**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from src.agent.graph import get_graph
from src.agent.prompts import validate_input

app = FastAPI()
graph = get_graph()
sessions: dict = {}

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

@app.post("/chat")
def chat(req: ChatRequest):
    is_valid, error = validate_input(req.message)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)
    state = sessions.get(req.session_id, {"messages": [], "user_profile": {}, "daily_log": {}})
    state["messages"].append(HumanMessage(content=req.message))
    result = graph.invoke(state)
    sessions[req.session_id] = result
    return {"response": result["messages"][-1].content}
```

**2. Add to `requirements.txt`:**
```
fastapi>=0.115.0
uvicorn>=0.30.0
```

**3. Run on EC2:**
```bash
pip install fastapi uvicorn
uvicorn api:app --host 0.0.0.0 --port 8000
```

**4. Open port 8000** in the EC2 security group inbound rules.

**5. Test it:**
```bash
curl -X POST http://<ec2-ip>:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How many calories in an apple?", "session_id": "user-1"}'
```

---

### Keep it running with systemd

```bash
sudo tee /etc/systemd/system/nutrition-agent.service << 'EOF'
[Unit]
Description=Nutrition Advisor Agent
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/nutritionalAgent
EnvironmentFile=/home/ec2-user/nutritionalAgent/.env
ExecStart=/home/ec2-user/nutritionalAgent/.venv/bin/uvicorn api:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable nutrition-agent
sudo systemctl start nutrition-agent

# Check status
sudo systemctl status nutrition-agent
```

---

### Recommended production architecture

```
Internet
    │
    ▼
Application Load Balancer  (HTTPS port 443)
    │
    ▼
EC2 Auto Scaling Group  (t3.small, Amazon Linux 2023)
    │  uvicorn api:app --port 8000
    │
    ▼
AWS Secrets Manager  ←── ANTHROPIC_API_KEY stored securely
```

Store the API key in **AWS Secrets Manager** instead of `.env`:
```bash
aws secretsmanager create-secret \
  --name nutrition-agent/anthropic-key \
  --secret-string "sk-ant-..."
```

Fetch it at startup using `boto3`:
```python
import boto3, json

def get_api_key():
    client = boto3.client("secretsmanager", region_name="eu-west-1")
    secret = client.get_secret_value(SecretId="nutrition-agent/anthropic-key")
    return secret["SecretString"]
```

---

### Cost estimate

| Setup | Est. monthly cost |
|---|---|
| `t3.micro` (AWS free tier, first 12 months) | ~$0 |
| `t3.small` (always on) | ~$15 |
| `t3.small` + Application Load Balancer | ~$25 |

---

## License

MIT

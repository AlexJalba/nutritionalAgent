"""CLI entry point for the Nutrition Advisor Agent."""
import os
import sys
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

load_dotenv()

# Fail fast if API key is missing
_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
if not _API_KEY or _API_KEY.startswith("sk-ant-your"):
    print("Error: ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your key.")
    sys.exit(1)

from src.agent.graph import get_graph  # noqa: E402 — import after env check
from src.agent.prompts import validate_input  # noqa: E402


def run_cli() -> None:
    graph = get_graph()
    state: dict = {"messages": [], "user_profile": {}, "daily_log": {}}

    print("=" * 60)
    print("  Nutrition Advisor Agent")
    print("  Powered by LangChain + Claude")
    print("  Type 'quit' or 'exit' to stop.")
    print("=" * 60)
    print()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye! Stay healthy.")
            break

        is_valid, error_msg = validate_input(user_input)
        if not is_valid:
            print(f"Agent: {error_msg}\n")
            continue

        state["messages"].append(HumanMessage(content=user_input))

        try:
            result = graph.invoke(state)
            state = result
            last_message = result["messages"][-1]
            print(f"Agent: {last_message.content}\n")
        except Exception as e:
            print(f"Agent: Sorry, I encountered an error: {str(e)[:300]}\n")


if __name__ == "__main__":
    run_cli()

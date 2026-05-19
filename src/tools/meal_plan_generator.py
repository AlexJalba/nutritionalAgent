"""Meal plan generator — returns a structured meal suggestion prompt for the LLM."""
from langchain_core.tools import tool


@tool
def generate_meal_plan(
    daily_calories: int,
    goal: str,
    dietary_restrictions: str = "",
    meals_per_day: int = 3,
) -> str:
    """Generate a meal plan suggestion based on calorie target and dietary preferences.

    Args:
        daily_calories: Target daily calorie intake.
        goal: Dietary goal — 'lose', 'maintain', or 'gain'.
        dietary_restrictions: Comma-separated restrictions e.g. 'vegan, gluten-free' (optional).
        meals_per_day: Number of meals per day (2-6).

    Returns:
        A structured meal plan template.
    """
    if daily_calories <= 0:
        return "Error: daily_calories must be positive."
    if goal not in ("lose", "maintain", "gain"):
        return "Error: goal must be 'lose', 'maintain', or 'gain'."
    meals_per_day = max(2, min(6, meals_per_day))

    per_meal = daily_calories // meals_per_day
    restrictions_note = f" (restrictions: {dietary_restrictions.strip()[:200]})" if dietary_restrictions.strip() else ""

    lines = [f"Meal plan for goal '{goal}'{restrictions_note} — {daily_calories} kcal/day:"]
    meal_names = ["Breakfast", "Morning Snack", "Lunch", "Afternoon Snack", "Dinner", "Evening Snack"]
    for i in range(meals_per_day):
        lines.append(f"  {meal_names[i]}: ~{per_meal} kcal")
    lines.append("Please suggest specific foods for each meal above.")
    return "\n".join(lines)

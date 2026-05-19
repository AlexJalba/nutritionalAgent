"""Calorie and TDEE calculator using Mifflin-St Jeor equation."""
from langchain_core.tools import tool

_ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}

_GOAL_ADJUSTMENTS = {
    "lose": -500,
    "maintain": 0,
    "gain": 500,
}


@tool
def calorie_calculator(
    age: int,
    weight_kg: float,
    height_cm: float,
    gender: str,
    activity_level: str = "moderate",
    goal: str = "maintain",
) -> str:
    """Calculate daily calorie needs (TDEE) using Mifflin-St Jeor equation.

    Args:
        age: Age in years (1-120).
        weight_kg: Body weight in kilograms.
        height_cm: Height in centimetres.
        gender: 'male' or 'female'.
        activity_level: One of sedentary, light, moderate, active, very_active.
        goal: One of lose, maintain, gain.

    Returns:
        BMR, TDEE, and recommended daily calories as a string.
    """
    if not (1 <= age <= 120):
        return "Error: age must be between 1 and 120."
    if weight_kg <= 0 or height_cm <= 0:
        return "Error: weight and height must be positive numbers."
    gender = gender.lower().strip()
    if gender not in ("male", "female"):
        return "Error: gender must be 'male' or 'female'."
    activity_level = activity_level.lower().strip()
    if activity_level not in _ACTIVITY_MULTIPLIERS:
        return f"Error: activity_level must be one of {list(_ACTIVITY_MULTIPLIERS)}."
    goal = goal.lower().strip()
    if goal not in _GOAL_ADJUSTMENTS:
        return f"Error: goal must be one of {list(_GOAL_ADJUSTMENTS)}."

    if gender == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    tdee = bmr * _ACTIVITY_MULTIPLIERS[activity_level]
    recommended = tdee + _GOAL_ADJUSTMENTS[goal]

    return (
        f"BMR: {bmr:.0f} kcal/day | "
        f"TDEE ({activity_level}): {tdee:.0f} kcal/day | "
        f"Recommended for goal '{goal}': {recommended:.0f} kcal/day"
    )

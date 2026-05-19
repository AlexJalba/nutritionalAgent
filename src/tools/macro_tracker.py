"""In-session macro and calorie tracker."""
from langchain_core.tools import tool

# In-memory daily log — reset per agent session via state injection
_daily_log: dict = {"calories": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0, "entries": []}


def reset_daily_log() -> None:
    """Reset the tracker (called on session start or new day)."""
    _daily_log.update({"calories": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0, "entries": []})


@tool
def log_food(food_name: str, calories: float, protein_g: float, carbs_g: float, fat_g: float) -> str:
    """Log a food item to today's macro tracker.

    Args:
        food_name: Name of the food eaten.
        calories: Calories consumed.
        protein_g: Protein in grams.
        carbs_g: Carbohydrates in grams.
        fat_g: Fat in grams.

    Returns:
        Updated daily totals.
    """
    if calories < 0 or protein_g < 0 or carbs_g < 0 or fat_g < 0:
        return "Error: nutritional values cannot be negative."

    _daily_log["calories"] += calories
    _daily_log["protein_g"] += protein_g
    _daily_log["carbs_g"] += carbs_g
    _daily_log["fat_g"] += fat_g
    _daily_log["entries"].append(food_name.strip()[:100])

    return (
        f"Logged '{food_name}'. Daily totals: "
        f"{_daily_log['calories']:.0f} kcal | "
        f"protein {_daily_log['protein_g']:.1f}g | "
        f"carbs {_daily_log['carbs_g']:.1f}g | "
        f"fat {_daily_log['fat_g']:.1f}g"
    )


@tool
def get_daily_summary() -> str:
    """Get today's logged macro and calorie totals.

    Returns:
        Summary of all food logged today.
    """
    if not _daily_log["entries"]:
        return "No food logged today yet."

    entries = ", ".join(_daily_log["entries"])
    return (
        f"Today's log ({len(_daily_log['entries'])} items: {entries}): "
        f"{_daily_log['calories']:.0f} kcal | "
        f"protein {_daily_log['protein_g']:.1f}g | "
        f"carbs {_daily_log['carbs_g']:.1f}g | "
        f"fat {_daily_log['fat_g']:.1f}g"
    )

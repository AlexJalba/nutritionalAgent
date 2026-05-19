"""Nutrition lookup tool — queries USDA FoodData Central API."""
import httpx
from langchain_core.tools import tool

_USDA_BASE = "https://api.nal.usda.gov/fdc/v1"
_MAX_QUERY_LEN = 200


def _get_nutrient(nutrients: list[dict], nutrient_id: int) -> float:
    for n in nutrients:
        if n.get("nutrientId") == nutrient_id:
            return round(n.get("value", 0), 2)
    return 0.0


@tool
def nutrition_lookup(food_query: str) -> str:
    """Look up nutrition information for a food item.

    Args:
        food_query: Name of the food to look up (e.g. 'banana', 'chicken breast').

    Returns:
        Nutritional information per 100g or a not-found message.
    """
    food_query = food_query.strip()[:_MAX_QUERY_LEN]
    if not food_query:
        return "Error: food query cannot be empty."

    try:
        search_resp = httpx.get(
            f"{_USDA_BASE}/foods/search",
            params={"query": food_query, "pageSize": 1, "dataType": "SR Legacy,Foundation"},
            timeout=10,
        )
        search_resp.raise_for_status()
        foods = search_resp.json().get("foods", [])
        if not foods:
            return f"No nutrition data found for '{food_query}'. Try a more specific name."

        food = foods[0]
        nutrients = food.get("foodNutrients", [])

        # USDA nutrient IDs: 1008=Energy(kcal), 1003=Protein, 1005=Carbs, 1004=Fat, 1079=Fiber
        result = {
            "food": food.get("description", food_query),
            "calories_kcal": _get_nutrient(nutrients, 1008),
            "protein_g": _get_nutrient(nutrients, 1003),
            "carbs_g": _get_nutrient(nutrients, 1005),
            "fat_g": _get_nutrient(nutrients, 1004),
            "fiber_g": _get_nutrient(nutrients, 1079),
            "per": "100g",
        }
        return (
            f"{result['food']} (per {result['per']}): "
            f"{result['calories_kcal']} kcal, "
            f"protein {result['protein_g']}g, "
            f"carbs {result['carbs_g']}g, "
            f"fat {result['fat_g']}g, "
            f"fiber {result['fiber_g']}g"
        )
    except httpx.TimeoutException:
        return "Error: nutrition lookup timed out. Please try again."
    except Exception as e:
        return f"Error looking up '{food_query}': {str(e)[:200]}"

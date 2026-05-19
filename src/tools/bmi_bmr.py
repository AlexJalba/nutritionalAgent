"""BMI and BMR calculator."""
from langchain_core.tools import tool


@tool
def bmi_bmr_calculator(
    weight_kg: float,
    height_cm: float,
    age: int,
    gender: str,
) -> str:
    """Calculate BMI and Basal Metabolic Rate (BMR).

    Args:
        weight_kg: Body weight in kilograms.
        height_cm: Height in centimetres.
        age: Age in years.
        gender: 'male' or 'female'.

    Returns:
        BMI value with classification and BMR.
    """
    if weight_kg <= 0 or height_cm <= 0:
        return "Error: weight and height must be positive."
    if not (1 <= age <= 120):
        return "Error: age must be between 1 and 120."
    gender = gender.lower().strip()
    if gender not in ("male", "female"):
        return "Error: gender must be 'male' or 'female'."

    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)

    if bmi < 18.5:
        classification = "Underweight"
    elif bmi < 25:
        classification = "Normal weight"
    elif bmi < 30:
        classification = "Overweight"
    else:
        classification = "Obese"

    if gender == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    return (
        f"BMI: {bmi:.1f} ({classification}) | "
        f"BMR: {bmr:.0f} kcal/day (calories needed at complete rest)"
    )

"""Pydantic models for nutrition data."""
from pydantic import BaseModel, Field


class NutritionInfo(BaseModel):
    food_name: str
    calories: float = Field(ge=0)
    protein_g: float = Field(ge=0)
    carbs_g: float = Field(ge=0)
    fat_g: float = Field(ge=0)
    fiber_g: float = Field(ge=0, default=0)
    serving_size_g: float = Field(gt=0, default=100)


class UserProfile(BaseModel):
    age: int = Field(gt=0, lt=150)
    weight_kg: float = Field(gt=0)
    height_cm: float = Field(gt=0)
    gender: str  # "male" or "female"
    activity_level: str = "moderate"  # sedentary, light, moderate, active, very_active
    goal: str = "maintain"  # lose, maintain, gain
    dietary_restrictions: list[str] = Field(default_factory=list)


class DailyLog(BaseModel):
    calories: float = 0
    protein_g: float = 0
    carbs_g: float = 0
    fat_g: float = 0
    entries: list[str] = Field(default_factory=list)

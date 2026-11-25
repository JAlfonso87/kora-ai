from typing import Literal
from pydantic import BaseModel, Field

from app.context_module.nutritional_profile.models import UserProfile, Preferences, Restrictions

class MealRegistrationInput(BaseModel):
    meal_description: str = Field(
        description = "Meal description in natural language."
    )

class GoalArchtypeInput(BaseModel):
    primary_goal: Literal["weight_loss", "muscle_gain", "maintenance"] = Field(
        description="User's main nutritional goal.",
    )

class ProteinQueryRequirements(BaseModel):
    user_profile: UserProfile = Field(
        description="Information about the user's age, sex, weight, or height."
    )
    food_preferences: Preferences | None = Field(
        default=None,
        description="Information about the user's food preferences",
    )
    food_restrictions: Restrictions | None = Field(
        default=None,
        description="Information about the user's food restrictions related to acquirability, personal dislikes or allergies.",
    )
    primary_goal: Literal["weight_loss", "muscle_gain", "maintenance"] = Field(
        description="User's main nutritional goal.",
    )
    protein_g: float = Field(
        gt=0,
        description="Protein consumed by the current moment expressed in grams.",
    )
    protein_target_g: float = Field(
        gt=0,
        description="User's protein target expressed in grams.",
    )

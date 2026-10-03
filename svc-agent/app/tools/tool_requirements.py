from pydantic import BaseModel, Field
from typing import Literal
from app.nutritional_context.nutritional_context_models import UserProfile, Goals, CurrentConsumption, Preferences, Restrictions

class NutritionalContextUpdate(BaseModel):
    user_profile: UserProfile | None = Field(
        default=None,
        description="New or updated information about the user's age, sex, weight, or height."
    )

    goals: Goals | None = Field(
        default=None,
        description="New or updated information about the user's nutritional goals or nutrient targets."
    )

    current_consumption: CurrentConsumption | None = Field(
        default=None,
        description="Nutrients the user has consumed so far today or during the current tracking period."
    )

    food_preferences: Preferences | None = Field(
        default=None,
        description="New or updated information about the user's food preferences",
    )

    food_restrictions: Restrictions | None = Field(
        default=None,
        description="New or updated information about the user's food restrictions related to acquirability, personal dislikes or allergies.",
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
    ),


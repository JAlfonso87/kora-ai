from pydantic import BaseModel, Field, field_validator
from typing import Literal
from app.context_module.nutritional_profile.models import (
    UserProfile, 
    Goals, 
    CurrentConsumption, 
    Preferences, 
    Restrictions, 
    NutritionalContext
)

class AgentRequest(BaseModel):
    message: str
    session_id: str | None = None
    nutritional_context: NutritionalContext | None = None

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Message cannot be empty")

        return value.strip()


class AgentResponse(BaseModel):
    response: str
    session_id: str | None = None

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
    )


class RAGQueryRequirements(BaseModel):
    query: str = Field(
        min_length=1,
        description="Question or topic about nutrition for which relevant information must be retrieved from the knowledge base."
    )

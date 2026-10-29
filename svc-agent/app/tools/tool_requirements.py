from pydantic import BaseModel, Field
from typing import Literal,Any
from app.context_module.nutritional_context_models import UserProfile, Goals, CurrentConsumption, Preferences, Restrictions
from pydantic import BaseModel, Field, ConfigDict
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


class BayesEvidenceSignals(BaseModel):
    """Only evidence identifiers registered by the HU-012 scenarios."""
    model_config = ConfigDict(extra="forbid")

    macros_ok: bool | None = None
    restrictions_ok: bool | None = None
    preferred_food: bool | None = None
    protein_below_target: bool | None = None
    calories_below_target: bool | None = None
    balanced_goal: bool | None = None
    high_vision_confidence: bool | None = None
    nutrition_data_available: bool | None = None
    context_complete: bool | None = None
    evidence_consistent: bool | None = None


class BayesReasoningRequirements(BaseModel):
    scenario_id: Literal[
        "meal_suitability",
        "nutritional_priority",
        "recommendation_confidence",
    ] = Field(description="Bayesian scenario to evaluate.")
    evidence: BayesEvidenceSignals | None = Field(
        default=None,
        description=(
            "Optional evidence using only registered boolean fields. For meal_suitability use "
            "macros_ok, restrictions_ok, preferred_food. For nutritional_priority use "
            "protein_below_target, calories_below_target, balanced_goal. For "
            "recommendation_confidence use high_vision_confidence, nutrition_data_available, "
            "context_complete, evidence_consistent. Do not invent food-specific keys such as "
            "oatmeal_high_carb or oatmeal_high_protein. Prefer omitting evidence when the "
            "processor can derive it from the stored nutritional context. Omit unknown signals."
        ),
    )
    context: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Optional decision-specific signals explicitly grounded in available context. "
            "Do not repeat or invent profile, intake, goal, or restriction values."
        ),
    )

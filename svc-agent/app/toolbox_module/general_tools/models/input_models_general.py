from typing import Literal, Any
from pydantic import BaseModel, Field, ConfigDict, model_validator
from enum import Enum

from app.context_module.nutritional_profile.models import UserProfile, Goals, CurrentConsumption, Preferences, Restrictions, RemainingNutrients
from app.context_module.food_profile.models import Meal

from app.inference_module.operators import Operator

from app.ai_module.agents.available_queries import PlannerAvailableQueries

""" -- GENERAL TOOLS -- """

class SubAgentToolRequest(BaseModel):
    message: str = Field(
        description = "User's message that triggered the activation of the sub-agent."
    )
    contextual_messages: str = Field(
        description = "Brief list of previous messages before tool call to give simple context."
    )
    nutritional_context: str = Field(
        description = "User's nutritional context."
    )
    query: PlannerAvailableQueries = Field(
        description = "Simple instruction given by the main agent to the sub-agent."
    )
    
class NutritionalContextUpdate(BaseModel):
    user_profile: UserProfile | None = Field(
        default=None,
        description="New or updated information about the user's age, sex, weight, or height."
    )

    goals: Goals | None = Field(
        default=None,
        description="New or updated information about the user's nutritional goals or nutrient targets."
    )

    remaining_nutrients: RemainingNutrients | None = Field(
        default = None,
        description = "Nutrients left to reach user's daily goals."
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

class FoodContextUpdate(BaseModel):
    meals: list[Meal] | None = Field(
        default=None,
        description="Updated list of today's meals registered by the user."
    )

class PlannerQuery(BaseModel):
    query: PlannerAvailableQueries = Field(
        description = "Brief query sent from the main agent to the sub-agent"
    )

""" -- PROBABILISTIC ANALYSIS TOOLS -- """

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

""" -- RETRIEVAL AUGMENTED GENERATION TOOLS (RAG) -- """

class RAGQueryRequirements(BaseModel):
    query: str = Field(
        min_length=1,
        description="Question or topic about nutrition for which relevant information must be retrieved from the knowledge base."
    )

""" -- ARTIFICIAL VISION TOOLS -- """

class ArtificialVisionInput(BaseModel):
    image_conversion_status: Literal["success", "failed"] = Field(
        description = "Describes wether the conversion to bytes was successful or, given the case, unsuccessful due to restrictions or errors."
    )
    image_conversion_annotations: str = Field(
        description = "Extra details referring to the status of the image conversion to bytes."
    )
    image_id: str | None = Field(
        description = "Unique ID associated with an image, used to get the byte map of said image."
    )

class ImageTemplate(BaseModel):
    width: int = Field(
        description = "Image width described in px.",
        gt = 0
    )
    height: int = Field(
        description = "Image height described in px.",
        gt = 0
    )
    total_px: int = Field(
        description = "Image's total amount of pixels.",
        gt = 0,
        lt = 20_000_000
    )

""" -- INFERENCE TOOLS -- """

class TruthValue(str, Enum):
    TRUE = "true"
    FALSE = "false"
    UNKNOWN = "unknown"

class Condition(BaseModel):
    fact: str = Field(
        min_length=1,
        description="Identifier of the fact in the facts base.",
    )

    operator: Operator

    value: Any = None

    value_from_fact: str | None = None

    @model_validator(mode="after")
    def validate_condition(self):
        if self.value_from_fact is not None and not self.value_from_fact.strip():
            raise ValueError("'value_from_fact' cannot be empty.")

        if self.operator in {"contains_any_fact", "in_fact"}:
            if not self.value_from_fact:
                raise ValueError(
                    f"Operator '{self.operator}' requires 'value_from_fact'."
                )
            if self.value is not None:
                raise ValueError(
                    f"Operator '{self.operator}' uses 'value_from_fact', "
                    "not 'value'."
                )

        elif self.value_from_fact is not None:
            if self.operator not in {"eq", "ne", "gt", "gte", "lt", "lte"}:
                raise ValueError(
                    f"Operator '{self.operator}' does not support "
                    "'value_from_fact'."
                )
            if self.value is not None:
                raise ValueError(
                    "Use either 'value' or 'value_from_fact', not both."
                )

        elif self.operator not in {"exists", "unknown_or_missing"}:
            if self.value is None:
                raise ValueError(
                    f"Operator '{self.operator}' requires a non-None value "
                    "or a valid 'value_from_fact'."
                )

        if self.operator in {"exists", "unknown_or_missing"}:
            if self.value is not None and not isinstance(self.value, bool):
                raise ValueError(
                    f"Operator '{self.operator}' accepts only a boolean "
                    "value when one is provided."
                )
            if self.value_from_fact is not None:
                raise ValueError(
                    f"Operator '{self.operator}' does not use "
                    "'value_from_fact'."
                )

        return self


class Conclusion(BaseModel):
    type: str = Field(min_length=1)
    code: str = Field(min_length=1)
    message: str = Field(min_length=1)


class Rule(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    category: str = "general"
    description: str = ""
    conditions: list[Condition] = Field(min_length=1)
    conclusion: Conclusion
    priority: int = 100
    enabled: bool = True
    notes: str | None = None


class ConditionResult(BaseModel):
    fact: str
    operator: str
    expected: Any = None
    actual: Any = None
    status: TruthValue
    explanation: str
    missing_facts: list[str] = Field(default_factory=list)


class RuleResult(BaseModel):
    rule_id: str
    rule_name: str
    status: TruthValue
    conclusion: Conclusion | None = None
    conditions: list[ConditionResult]
    missing_facts: list[str] = Field(default_factory=list)


class EvaluationResult(BaseModel):
    activated_rules: list[str] = Field(default_factory=list)
    conclusions: list[Conclusion] = Field(default_factory=list)
    rule_results: list[RuleResult] = Field(default_factory=list)
    missing_facts: list[str] = Field(default_factory=list)

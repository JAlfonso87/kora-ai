from typing import Literal
from pydantic import BaseModel, Field


class FoodEvaluationContext(BaseModel):
    food_name: str = Field(
        description="Generic name of the current food."
    )

    quantity_g: float | None = Field(
        description="Estimated quantity of the current food expressed in grams.",
        default=None,
        gt=0,
    )

    calories_kcal: float | None = Field(
        description="Estimated calorie intake based on food quantity, expressed in kilocalories.",
        default=None,
        ge=0,
    )

    protein_g: float | None = Field(
        description="Estimated protein intake based on food quantity, expressed in grams.",
        default=None,
        ge=0,
    )

    ingredients: list[str] | None = Field(
        description="If it's a composite food (involves ingredients) lists every single ingredient involved in its elaboration.",
        default=None,
    )
    allergens: list[str] | None = Field(
        description="If it's a composite food (involves ingredients) lists every possible allergen involved in its elaboration.",
        default=None,
    )

    data_source: Literal[
        "llm_estimate",
        "user_provided",
        "unknown",
    ] = "unknown"
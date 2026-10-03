from pydantic import BaseModel, Field
from typing import Literal


class UserProfile(BaseModel):
    age: int | None = Field(
        default=None,
        gt=0,
        description="User's age expressed in years.",
    ) 
    sex: Literal["male", "female"] | None = Field(
        default=None,
        description="User's biological sex.",
    )
    weight_kg: float | None = Field(
        default=None,
        gt=0,
        description="User's weight expressed in kilograms.",
    )
    height_cm: float | None = Field(
        default=None,
        gt=0,
        description="User's height expressed in centimeters.",
    )


class Goals(BaseModel):
    primary_goal: Literal["weight_loss", "muscle_gain", "maintenance"] | None = Field(
        default=None,
        description="User's main nutritional goal.",
    )
    calorie_target_kcal: float | None = Field(
        default=None,
        gt=0,
        description="User's calorie target expressed in kilocalories.",
    )
    protein_target_g: float | None = Field(
        default=None,
        gt=0,
        description="User's protein target expressed in grams.",
    )


class CurrentConsumption(BaseModel):
    calories_kcal: float | None = Field(
        default=None,
        gt=0,
        description="Calories consumed by the current moment expressed in kilocalories.",
    )
    protein_g: float | None = Field(
        default=None,
        gt=0,
        description="Protein consumed by the current moment expressed in grams.",
    )


class RemainingNutrients(BaseModel):
    calories_kcal: float | None = Field(
        default=None,
        gt=0,
        description="Calories left to reach calorie goal expressed in kilocalories.",
    )
    protein_g: float | None = Field(
        default=None,
        gt=0,
        description="Protein left to reach protein goal expressed in grams.",
    )


class Preferences(BaseModel):
    preferred_foods: list[str] = Field(
        default_factory=list,
        description="List including all of user's preferred foods.",
    )


class Restrictions(BaseModel):
    avoided_foods: list[str] = Field(
        default_factory=list,
        description="List including all of user's disliked foods.",
    )
    unavailable_foods: list[str] = Field(
        default_factory=list,
        description="List including all foods not easily acquirable by the user, the model must search alternatives with similar nutritional value.",
    )
    allergies: list[str] = Field(
        default_factory=list,
        description="List including all foods that trigger an allergic reaction to the user.",
    )

class NutritionalContext(BaseModel):
    user_profile: UserProfile | None = None
    goals: Goals | None = None
    current_consumption: CurrentConsumption | None = None
    remaining_nutrients: RemainingNutrients | None = None
    food_preferences: Preferences | None = Field(
        default=None,
        description="Foods that for whatever reason, the user prefers over other foods.",
    )
    food_restrictions: Restrictions | None = Field(
        default=None,
        description="Foods that the user avoids for reasons related to acquirability, personal dislikes or allergies.",
    )

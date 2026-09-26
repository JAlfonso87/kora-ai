from pydantic import BaseModel, Field
from typing import Literal

class UserProfile(BaseModel):
    age: int = Field(
        gt = 0,
        description= "User's expressed in years."
    )
    sex: Literal["male", "female"] = Field(
        description = "User's biological sex."
    )
    weight_kg: float = Field(
        gt = 0,
        description = "User's weight expressed in kilograms."
    )
    height_cm: float = Field(
        gt = 0,
        description = "User's height expressed in centimeters."
    )


class Goals(BaseModel):
    primary: Literal["weight_loss", "muscle_gain", "maintenance"] = Field(
        description = "User's main nutritional goal."
    )
    calorie_target_kcal: float = Field(
        gt = 0,
        description = "User's calorie target expressed in kilocalories."
    )
    protein_target_g: float = Field(
        gt = 0,
        description = "User's protein target expressed in grams."
    )


class CurrentConsumption(BaseModel):
    calories_kcal: float = Field(
        gt = 0,
        description = "Calories consumed by the current moment expressed in kilocalories."
    )
    protein_g: float = Field(
        gt = 0,
        description = "Protein consumed by the current moment expressed in grams."
    )


class RemainingNutrients(BaseModel):
    calories_kcal: float = Field(
        gt = 0,
        description = "Calories left to reach calorie goal expressed in kilocalories."
    )
    protein_g: float = Field(
        gt = 0,
        description = "Protein left to reach protein goal expressed in grams."
    )


class Preferences(BaseModel):
    preferred_foods: list[str] = Field(
        description = "List including all of user's preferred foods."
    )


class Restrictions(BaseModel):
    avoided_foods: list[str] = Field(
        description = "List including all of user's disliked foods."
    )
    unavailable_foods = list[str] = Field(
        description = "List including all foods not easily acquirable by the user, subject to exchange with others of similar nutritional value."
    )
    allergies: list[str] = Field(
        description = "List including all foods that must not be recommended under any circumstance given it poses severe risk to the user's health."
    )

class NutritionalContext(BaseModel):
    user_profile = UserProfile
    goals = Goals
    current_consumption = CurrentConsumption
    remaining_nutrients = RemainingNutrients
    preferences = Preferences
    restrictions = Restrictions
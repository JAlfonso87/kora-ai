from typing import Literal
from pydantic import BaseModel, Field

class NutritionalValues(BaseModel):
    calories_kcal: float = Field(
        description = "Calories per 100g of ingredient expressed in kcal",
        ge=0
    )
    protein_g: float = Field(
        description = "Protein per 100g of ingredient expressed in grams.",
        ge=0
    )
    carbohydrates_g: float = Field(
        description = "Carbohydrates per 100 grams of ingredient expressed in grams.",
        ge=0
    )
    fats_g: float = Field(
        description = "Fats per 100 grams of ingredient expressed in grams.",
        ge=0
    )

class Ingredient(BaseModel):
    name: str = Field(
        description = "Ingredient's name"
    )
    quantity_g: float = Field(
        description = "Ingredient's quantity expressed in grams.",
        gt = 0
    )
    nutrients_per_100g: NutritionalValues = Field(
        description = "Nutritional values per 100 grams of ingredient."
    )

class Food(BaseModel):
    name: str = Field(
        description = "Food's name"
    )
    classification: Literal["regular", "processed"] = Field(
        description = "Classification of the food's origins. Being 'regular' the proper classification for proper foods like homemade ones," \
        "and 'processed' being the proper classification for foods like packaged snacks, desserts, and others."
    )
    ingredients: list[Ingredient] = Field(
        description = "List of the food's ingredients."
    )
    brand: str | None = Field(
        default = None,
        description = "Food's brand."
    )
    
class Meal(BaseModel):
    name: str = Field(
        description = "Common name of the whole meal given by the user (may vary)"
    )
    involved_foods: list[Food] = Field(
        description = "List of foods that form part of the whole meal."
    )

class FoodContext(BaseModel):
    meals: list[Meal] = Field(
        default = [],
        description = "List of today's meals registered by the user."
    )

from pydantic import BaseModel


class FoodClassificationResult(BaseModel):
    food: str
    score: float
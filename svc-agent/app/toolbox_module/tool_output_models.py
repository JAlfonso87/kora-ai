from typing import Literal
from pydantic import BaseModel, Field

""" -- ARTIFICIAL VISION TOOLS -- """

class VisionPrediction(BaseModel):
    food: str
    score: float
    score_type: Literal["svm_decision_score"]

class VisionToolResult(BaseModel):
    success: bool
    status: Literal["identified", "uncertain", "error"]
    predictions: list[VisionPrediction] = Field(default_factory=list)
    message: str
    error_code: str | None = None

class FoodClassificationResult(BaseModel):
    food: str
    score: float
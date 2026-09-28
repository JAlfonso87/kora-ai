from pydantic import BaseModel, field_validator
from app.nutritional_context import NutritionalContext


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

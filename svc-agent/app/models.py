from pydantic import BaseModel, field_validator
from nutritional_context import NutritionalContext

class AgentRequest(BaseModel):
    message: str
    nutritional_context: NutritionalContext | None = None

    @field_validator("message")
    @classmethod
    def validate_message(cls, value):
        if not value.strip():
            raise ValueError("Message cannot be empty")

        return value


class AgentResponse(BaseModel):
    response: str
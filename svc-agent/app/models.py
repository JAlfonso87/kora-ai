from pydantic import BaseModel, field_validator

class AgentRequest(BaseModel):
    message: str
    session_id: str | None = None

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Message cannot be empty")
        return value.strip()


class AgentResponse(BaseModel):
    response: str
    session_id: str | None = None

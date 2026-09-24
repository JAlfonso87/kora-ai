from pydantic import BaseModel, field_validator


class AgentRequest(BaseModel):
    message: str

    @field_validator("message")
    @classmethod
    def validate_message(cls, value):
        if not value.strip():
            raise ValueError("Message cannot be empty")

        return value


class AgentResponse(BaseModel):
    response: str
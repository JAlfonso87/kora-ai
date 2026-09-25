from fastapi import FastAPI, HTTPException

from models import AgentRequest, AgentResponse
from services.llm_service import generate_response


app = FastAPI(
    title="Kora AI - Agent Service",
    version="1.0.0",
)


@app.get("/")
def health_check():
    return {
        "message": "Kora AI Agent Service is running"
    }


@app.post("/agent/query", response_model=AgentResponse)
def query_agent(request: AgentRequest):

    try:
        response = generate_response(request.message)

        return AgentResponse(
            response=response
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to generate a response",
        )
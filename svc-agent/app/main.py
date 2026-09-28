from fastapi import FastAPI, HTTPException
from app.models import AgentRequest, AgentResponse
from app.services.llm_service import generate_response
from app.services.memory import clear_session

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
        response_text, session_id = generate_response(
            message=request.message,
            session_id=request.session_id,
            nutritional_context=request.nutritional_context,
        )

        return AgentResponse(
            response=response_text,
            session_id=session_id,
        )

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to generate a response",
        ) from exc


@app.delete("/agent/memory/{session_id}")
def reset_memory(session_id: str):
    """Borra el historial de una sesión (útil para pruebas)."""
    clear_session(session_id)
    return {"message": f"Memory for session '{session_id}' cleared"}

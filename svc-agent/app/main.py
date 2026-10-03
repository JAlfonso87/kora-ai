from fastapi import FastAPI, HTTPException
import logging, traceback
from fastapi.middleware.cors import CORSMiddleware
from app.models import AgentRequest, AgentResponse
from app.services.llm_service import generate_response
from app.services.memory import clear_session

app = FastAPI(
    title="Kora AI - Agent Service",
    version="1.0.0",
)

logger = logging.getLogger(__name__)
# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        )

        return AgentResponse(
            response=response_text,
            session_id=session_id,
        )

    except ValueError as exc:
        logger.error(
            "ValueError while generating response:\n"
            "  Type: %s\n"
            "  Message: %s\n"
            "  Traceback:\n%s",
            type(exc).__name__,
            str(exc),
            traceback.format_exc(),
        )
        raise HTTPException(
            status_code=400, 
            detail=(
                f"ValueError: {type(exc).__name__}: {exc}\n"
                f"Traceback:\n{traceback.format_exc()}"
            ),
        ) from exc
    
    except Exception as exc:
        logger.error(
            "Unexpected exception while generating response:\n"
            "  Type: %s\n"
            "  Message: %s\n"
            "  Traceback:\n%s",
            type(exc).__name__,
            str(exc),
            traceback.format_exc(),
        )
        raise HTTPException(
            status_code=500,
            detail=(
                f"Unexpected error: {type(exc).__name__}: {exc}\n"
                f"Traceback:\n{traceback.format_exc()}"
            ),
        ) from exc
    
@app.delete("/agent/memory/{session_id}")
def reset_memory(session_id: str):
    """Borra el historial de una sesión (útil para pruebas)."""
    clear_session(session_id)

    return {
        "message": f"Memory for session '{session_id}' cleared"
    }
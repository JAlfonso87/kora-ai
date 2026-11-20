from fastapi import FastAPI, HTTPException, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import json
import logging
import traceback
import uuid

from app.models import AgentResponse

from app.ai_module.agents.general.agent import GeneralAgent
from app.ai_module.memory_manager.memory import Memory
from app.ai_module.memory_manager.memory_tester import MemoryTester

from app.context_module.nutritional_profile.models import NutritionalContext

from app.toolbox_module.vision_tools.tool_functions_vision import IMAGE_DICT

app = FastAPI(
    title="Kora AI - Agent Service",
    version="1.0.0",
)

logger = logging.getLogger(__name__)
# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REQUEST_IMAGE_KEY = "request_image"

general_memory = Memory()
general_agent = GeneralAgent()

@app.get("/")
def health_check():
    return {
        "message": "Kora AI Agent Service is running"
    }

@app.get("/tests/memory")
async def test_memory():
    MemoryTester(str(uuid.uuid4())).start_test()
    return { "message": "RUNNING TESTS. CHECK SERVER CONSOLE FOR RESULTS."}

@app.post("/agent/query", response_model=AgentResponse)
async def query_agent(message: str = Form(...),
    session_id: str = Form(""),
    nutritional_context: str = Form(""),
    image: UploadFile | None = File(None),
    ):
        
    try:

        if not general_memory.session_id:
            general_memory.session_id = session_id

        if not general_agent.memory:
            general_agent.memory = general_memory

        # 1. Limpiar imagen anterior de esta "ranura"
        IMAGE_DICT.pop(REQUEST_IMAGE_KEY, None)

        # 2. Si viene imagen, guardarla en IMAGE_DICT
        if image is not None and image.filename:
            image_bytes = await image.read()
            if image_bytes:
                IMAGE_DICT[REQUEST_IMAGE_KEY] = image_bytes

        # 3. Parsear contexto nutricional (viene como string JSON)
        ctx = None
        if nutritional_context and nutritional_context.strip():
            try:
                ctx = NutritionalContext.model_validate(
                    json.loads(nutritional_context)
                )
            except Exception:
                ctx = None

        # 4. Llamar al agente (sin cambiar su firma)
        response_text, new_session_id, vision_result = general_agent.generate_response(
            message=message,
            session_id=session_id or None,
            nutritional_context=ctx,
        )

        return AgentResponse(
            response=response_text,
            session_id=new_session_id,
            vision_result=vision_result,
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
    if not general_memory.session_id:
        error = {
            "message": f"Could not clear history for session '{session_id}'.",
            "err_code": "INEXIXSTENT_MEMORY_INSTANCE"
        }
        return error
    else: 
        general_memory.clear_session()
        return { "message": f"Memory for session '{session_id}' has been cleared successfully." }
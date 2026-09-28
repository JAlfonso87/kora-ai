from dotenv import load_dotenv
import os
import uuid

from groq import Groq

from app.services.memory import get_history, add_message

load_dotenv()

client = Groq(api_key=os.getenv("LLM_API_KEY"))

SYSTEM_PROMPT = (
    "Eres Kora AI, un asistente especializado en nutrición. "
    "Usa el contexto nutricional del usuario cuando esté disponible. "
    "No inventes datos que no se te hayan proporcionado. "
    "No realices diagnósticos médicos ni generes dietas completas."
)


def _build_context_text(nutritional_context) -> str:
    """Convierte el contexto nutricional en texto legible para el LLM."""
    if nutritional_context is None:
        return ""

    parts: list[str] = []
    data = nutritional_context.model_dump(exclude_none=True)

    if not data:
        return ""

    parts.append("Contexto nutricional del usuario:")
    for key, value in data.items():
        parts.append(f"- {key}: {value}")

    return "\n".join(parts)


def generate_response(
    message: str,
    session_id: str | None = None,
    nutritional_context=None,
) -> tuple[str, str]:
    """
    Genera una respuesta del LLM usando memoria simple de conversación.

    Returns:
        (respuesta_del_llm, session_id_usado)
    """
    if not session_id:
        session_id = str(uuid.uuid4())

    history = get_history(session_id)

    messages: list[dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    context_text = _build_context_text(nutritional_context)
    if context_text:
        messages.append({"role": "system", "content": context_text})

    messages.extend(history)

    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model=os.getenv("LLM_MODEL"),
        messages=messages,
    )

    assistant_content = response.choices[0].message.content or ""

    add_message(session_id, "user", message)
    add_message(session_id, "assistant", assistant_content)

    return assistant_content, session_id

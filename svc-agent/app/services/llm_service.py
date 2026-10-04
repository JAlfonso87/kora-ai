from dotenv import load_dotenv
import os
import uuid

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.services.memory import get_history, add_message

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("LLM_API_KEY"),
    model=os.getenv("LLM_MODEL")
)

SYSTEM_PROMPT = (
    "You are Kora AI, an assistant specialized in nutrition. "
    "Analyze the user's request using the nutritional context provided when available. "
    "Use only the information available in the request, conversation history, and nutritional context. "
    "Do not invent or assume information that has not been provided. "
    "Generate a clear, relevant, and concise response based on the available context. "
    "Do not provide medical diagnoses or complete diet plans."
)

PROMPT_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("system", "Nutritional context:\n{nutritional_context}"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{message}"),
    ]
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

    context_text = _build_context_text(nutritional_context)

    prompt = PROMPT_TEMPLATE.invoke(
        {
            "message": message,
            "nutritional_context": context_text,
            "history": history,
        }
    )

    response = llm.invoke(prompt)

    assistant_content = response.content or ""

    add_message(session_id, "user", message)
    add_message(session_id, "assistant", assistant_content)

    return assistant_content, session_id

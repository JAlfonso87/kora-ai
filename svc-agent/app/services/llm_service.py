from dotenv import load_dotenv
import os, uuid, json
from groq import Groq

from app.services.memory import get_history, add_message
from app.tools.tool_calls import groq_tools
from app.tools.tool_handler import handle_tool_call
from app.nutritional_context.nutritional_context_management import get_context, save_context

load_dotenv()

client = Groq(api_key=os.getenv("LLM_API_KEY"))

SYSTEM_PROMPT = (
    "Eres Kora AI, un asistente especializado en nutrición. "
    "Usa el contexto nutricional del usuario cuando esté disponible. "
    "No inventes datos que no se te hayan proporcionado. "
    "No realices diagnósticos médicos ni generes dietas completas."
)

def generate_response(
    message: str,
    session_id: str | None = None,
) -> tuple[str, str]:
    """
    Genera una respuesta del LLM usando memoria simple de conversación.

    Returns:
        (respuesta_del_llm, session_id_usado)
    """
    if not session_id:
        session_id = str(uuid.uuid4())

    context = get_context(session_id)

    add_message(session_id, "user", message)

    history = get_history(session_id)

    messages: list[dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"CURRENT NUTRITIONAL CONTEXT: {context}"}
    ]

    messages.extend(history)

    while True:

        # Generation of LLM's first response after user's input
        response = client.chat.completions.create(
            model=os.getenv("LLM_MODEL"),
            messages = messages,
            tools = groq_tools,
        )
        msg = response.choices[0].message

        # Checks if obtained msg contains tool_calls. If not, returns msg's plain text.
        if not msg.tool_calls:
            assistant_content = msg.content or ""
            add_message(session_id, "assistant", assistant_content)
            return assistant_content, session_id
        
        # If msg contains tool_calls, the program proceeds with their execution process.

        # Information about the current tool instruction gets stored inside local messages memory.
        messages.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    }
                }
                for tool_call in msg.tool_calls
            ]
        })

        # Begins execution of each tool via tool_handler
        for tool_call in msg.tool_calls:
            print(" << RECUPERANDO CONTEXTO >> ")
            context = get_context(session_id)
            print(" << CONTEXTO RECUPERADO >> ")
            result = handle_tool_call(tool_call = tool_call, context = context)

            print(" << RESULT RECUPERADO >> ")
            print(result)

            # Guardar el resultado de la herramienta.
            print(" << GUARDANDO CONTEXTO >> ")
            save_context(session_id=session_id, context=result['context'])
            print(" << CONTEXTO GUARDADO >> ")
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result['content'], ensure_ascii=False)
            })


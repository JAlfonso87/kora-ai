import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from app.toolbox_module.general_tools.tool_functions_general import Tools

from app.context_module.nutritional_profile.manager import get_context, save_context

from app.toolbox_module.tool_input_models import NutritionalContextUpdate

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("LLM_API_KEY"),
    model=os.getenv("LLM_MODEL")
)

context_extractor = llm.with_structured_output(NutritionalContextUpdate)

def context_enforcer(session_id: str, messages: list):
    context = get_context(session_id)

    update = context_extractor.invoke([
        SystemMessage(content="""
            Analiza los últimos mensajes entre el usuario y el agente y extrae información
            contextual a partir de ellos cuando la misma sea proporcionada de manera directa o
            indirecta.

            Si el mensaje es un saludo, una pregunta casual o no contiene
            información nutricional relevante, devuelve todos los campos
            como null.

            Algunas inferencias son permitidas a partir de la información dada por el usuario.
            No elimines información existente.
        """),
        HumanMessage(content=f"""
            Contexto actual:
            {context.model_dump_json()}

            Últimos mensajes de la conversación:
            {messages}
        """)
    ])

    result = Tools.update_nutritional_context(context, update)

    save_context(
        session_id=session_id,
        context=result["context"]
    )

    return result
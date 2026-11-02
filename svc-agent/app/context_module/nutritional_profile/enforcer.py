import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from app.toolbox_module.functions.tool_functions import Tools

from app.context_module.nutritional_profile.manager import get_context, save_context

from app.toolbox_module.models.tool_requirements import NutritionalContextUpdate

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("LLM_API_KEY"),
    model=os.getenv("LLM_MODEL")
)

toolbox = Tools()

context_extractor = llm.with_structured_output(NutritionalContextUpdate)

def context_enforcer(session_id: str, message: str):
    context = get_context(session_id)

    update = context_extractor.invoke([
        SystemMessage(content="""
            Analiza el mensaje del usuario y extrae exclusivamente
            información nutricional nueva o modificada.

            Si el mensaje es un saludo, una pregunta casual o no contiene
            información nutricional relevante, devuelve todos los campos
            como null.

            No inventes información.
            No elimines información existente.
        """),
        HumanMessage(content=f"""
            Contexto actual:
            {context.model_dump_json()}

            Mensaje del usuario:
            {message}
        """)
    ])

    result = toolbox.update_nutritional_context(context, update)

    print(" << FORCEFULLY UPDATING CONTEXT... >> ")

    save_context(
        session_id=session_id,
        context=result["context"]
    )
    print(" << CONTEXT HAS BEEN SUCCESFULLY UPDATED >> ")

    return result
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from app.toolbox_module.general_tools.tool_functions_general import Tools

from app.context_module.food_profile.manager import FoodContextManager

from app.toolbox_module.general_tools.models.input_models_general import FoodContextUpdate

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("LLM_API_KEY"),
    model=os.getenv("LLM_MODEL")
)

context_extractor = llm.with_structured_output(FoodContextUpdate)

def food_context_enforcer(manager: FoodContextManager, session_id: str, messages: list):
    context = manager.get_context(session_id)
    update = context_extractor.invoke([
        SystemMessage(content="""
            Analiza los últimos mensajes producto de Tools en búsqueda de información referente
            al registro de alimentos.
            Toma los datos estructurados obtenidos de los mensajes de herramienta y aplica el modelo
            Pydantic cuando sea necesario.
        """),
        HumanMessage(content=f"""
            Contexto actual:
            {context.model_dump_json()}

            Últimos mensajes de la conversación:
            {messages}
        """)
    ])

    result = Tools.update_food_context(context, update)
    manager.save_context(session_id, result)
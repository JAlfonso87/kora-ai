import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from app.toolbox_module.general_tools.tool_functions_general import Tools

from app.context_module.nutritional_profile.manager import NutritionalContextManager

from app.toolbox_module.general_tools.models.input_models_general import NutritionalContextUpdate

from app.ai_module.agents.structurer.structurer_agent import StructurerAgent

def context_enforcer(manager: NutritionalContextManager, session_id: str, messages: list, consumption_update: bool = False, goal_update: bool = False):
    context = manager.get_context(session_id)
    structurer = StructurerAgent(NutritionalContextUpdate)
    update = structurer.invoke([
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

    result = Tools.update_nutritional_context(context, update, consumption_update, goal_update)
    manager.save_context(session_id, result)
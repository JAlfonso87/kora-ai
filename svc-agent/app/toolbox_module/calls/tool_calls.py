from app.toolbox_module.models.tool_requirements import (
    ProteinQueryRequirements,
    NutritionalContextUpdate,
    RAGQueryRequirements
)
from app.toolbox_module.functions.tool_functions import Tools
from app.toolbox_module.rag_tool import RAGTool

groq_context_tools = [
        {
        "type": "function",
        "function": {
            "name": "update_nutritional_context",
            "description": (
                "Analiza el mensaje actual del usuario para identificar "
                "información nutricional nueva o modificaciones del contexto. "
                "Si no existe información nutricional relevante, devuelve "
                "una actualización vacía. Nunca inventes información."
            ),
            "parameters": NutritionalContextUpdate.model_json_schema(),
        },
    },
]

groq_tools = [
    {
        "type": "function",
        "function": {
            "name": "protein_assistance_query",
            "description": (
                "Resuelve consultas sobre consumo de proteína utilizando "
                "el contexto nutricional disponible. Úsala cuando el usuario "
                "pregunte por sus necesidades de proteína, consumo actual, "
                "cantidad restante o recomendaciones relacionadas. "
                "Antes de ejecutarla, el contexto nutricional debe haber "
                "sido actualizado con la información nueva del mensaje, "
                "si existe. No inventes datos ausentes. Si falta información "
                "imprescindible para responder de forma fiable, identifica "
                "qué dato falta y solicita al usuario que lo proporcione."
            ),
            "parameters": ProteinQueryRequirements.model_json_schema(),
        },
    },
    {
        "type": "function",
        "function": {
            "name": "rag_query",
            "description": (
                "Busca información relevante en la base de conocimiento "
                "nutricional de Kora AI. Utilízala cuando el usuario "
                "pregunte por conceptos, evidencia, alimentos, nutrientes "
                "o información nutricional que requiera consultar las "
                "fuentes documentales. No inventes fuentes ni afirmes que "
                "la base contiene información que no fue recuperada."
            ),
            "parameters": RAGQueryRequirements.model_json_schema(),
        },
    }
]

tool_specs = {
    "protein_assistance_query": {
        "function": Tools.protein_assistance_query,
        "params_model": ProteinQueryRequirements
    },
    "update_nutritional_context": {
        "function": Tools.update_nutritional_context,
        "params_model": NutritionalContextUpdate
    },
    "rag_query": {
        "function": RAGTool().execute,
        "params_model": RAGQueryRequirements
    }
}

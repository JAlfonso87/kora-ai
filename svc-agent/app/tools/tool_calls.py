from app.tools.tool_requirements import ProteinQueryRequirements, NutritionalContextUpdate,BayesReasoningRequirements
from app.tools.tool_functions import Tools
from app.bayes import BAYES_TOOL_SCHEMA
groq_tools = [
    {
        "type": "function",
        "function": {
            "name": "update_nutritional_context",
            "description": (
                "Actualiza el contexto nutricional utilizando exclusivamente "
                "la información explícita proporcionada por el usuario en "
                "su mensaje actual. Extrae los datos disponibles para "
                "NutritionalContext, según lo permita el esquema. "
                "No inventes ni infieras datos personales no proporcionados. "
                "Si no hay información nueva relevante, no inventes cambios. "
                "Utiliza esta herramienta antes de responder cuando el "
                "mensaje aporte información nutricional nueva o actualice "
                "datos previos."
            ),
            "parameters": NutritionalContextUpdate.model_json_schema(),
        },
    },
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
            "name": BAYES_TOOL_SCHEMA["name"],
            "description": BAYES_TOOL_SCHEMA["description"],
            "parameters": BayesReasoningRequirements.model_json_schema(),
        },
    },
]

tool_specs = {
    "protein_assistance_query" : {
        "function": Tools.protein_assistance_query,
        "params_model": ProteinQueryRequirements
    },
    "update_nutritional_context" : {
        "function": Tools.update_nutritional_context,
        "params_model": NutritionalContextUpdate
    },
    "bayes_reasoning": {
        "function": Tools.bayes_reasoning_query,
        "params_model": BayesReasoningRequirements,
    },
}
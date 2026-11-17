from app.toolbox_module.general_tools.tool_functions_general import Tools
from app.toolbox_module.tool_input_models import (
    ProteinQueryRequirements,
    NutritionalContextUpdate,
)

tools_context = [
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

tools_general = [
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
]

tool_specs_general = {
    "protein_assistance_query": {
        "function": Tools.protein_assistance_query,
        "params_model": ProteinQueryRequirements
    },
    "update_nutritional_context": {
        "function": Tools.update_nutritional_context,
        "params_model": NutritionalContextUpdate
    },
}

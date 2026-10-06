from app.tools.tool_requirements import ProteinQueryRequirements, NutritionalContextUpdate
from app.tools.tool_functions import Tools

groq_tools = [
    {
        "type": "function",
        "function": {
            "name": "protein_assistance_query",
            "description": (
                "No debe ejecutarse sin antes intentar actualizar el contexto nutricional mediante la función 'update_nutritional_context'"
                "El usuario requiere asistencia nutricional referente al consumo de proteína. No inventes datos, si hay algún dato"
                "que necesites y haga falta para completar la tarea, hazlo saber al usuario directamente guiándolo para entregar dichos"
                "datos de la forma en que los necesitas y no procedas hasta tener los datos necesarios."
            ),
            "parameters":
                ProteinQueryRequirements.model_json_schema()
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_nutritional_context",
            "description": (
                "Extrae y actualiza el contexto nutricional a partir de la información "
                "explícitamente proporcionada por el usuario en su mensaje actual. "
                "Debes identificar cualquier información relevante para user_profile, goals, "
                "current_consumption, food_context o nutritional_context. "
                "No inventes información que el usuario no haya proporcionado. "
                "Esta herramienta debe ejecutarse antes de responder al usuario."
            ),
            "parameters": NutritionalContextUpdate.model_json_schema(),
        },
    }
]

tool_specs = {
    "protein_assistance_query" : {
        "function": Tools.protein_assistance_query,
        "params_model": ProteinQueryRequirements
    },
    "update_nutritional_context" : {
        "function": Tools.update_nutritional_context,
        "params_model": NutritionalContextUpdate
    }
}
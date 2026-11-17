from app.toolbox_module.tool_input_models import BayesReasoningRequirements
from app.toolbox_module.bayes_tools.tool_functions_bayes import BayesTool

tools_probabilistic = [
    {
        "type": "function",
        "function": {
            "name": "bayes_reasoning",
            "description": (
                "Aplica razonamiento probabilístico (Teorema de Bayes) para manejar "
                "incertidumbre en decisiones del agente de nutrición. "
                "Escenarios activos: meal_suitability, nutritional_priority y "
                "recommendation_confidence. Las restricciones críticas bloquean fuera de Bayes."
            ),
            "parameters": BayesReasoningRequirements.model_json_schema(),
        },
    },
]

tool_specs_probabilistic = {
    "bayes_reasoning": {
        "function": BayesTool.bayes_reasoning_query,
        "params_model": BayesReasoningRequirements,
    }
}
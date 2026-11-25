from app.toolbox_module.general_tools.tool_functions_general import Tools
from app.toolbox_module.general_tools.models.input_models_general import (
    NutritionalContextUpdate,
    PlannerQuery
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
            "name": "delegate_to_planner_agent",
            "description": (
                """
                Delegates nutrition-related tasks to the PlannerAgent, a specialized agent responsible for processing and analyzing information about the user's food intake, evaluating nutritional requirements, and developing personalized nutritional plans.

                The PlannerAgent is responsible for:

                Food Intake Analysis: Process and analyze information about the foods and meals consumed by the user, identifying food items, ingredients, quantities, portions, and estimated nutritional values.
                Nutritional Requirements Validation: Evaluate the user's nutritional intake against their established nutritional requirements and goals, identifying nutritional deficiencies, excesses, imbalances, and potential deviations from their targets.
                Nutritional Progress Assessment: Analyze the user's dietary progress over a given period and determine whether their current eating habits align with their nutritional objectives.
                Nutritional Plan Generation: Create personalized meal plans and dietary recommendations based on the user's nutritional requirements, food preferences, dietary restrictions, and available food intake information.
                Nutritional Recommendations: Provide actionable suggestions to improve the user's dietary habits and help them meet their nutritional goals.

                Delegation Guidelines:

                Delegate tasks involving food intake analysis, nutritional calculations, nutritional requirement validation, dietary progress assessment, or meal planning to this agent.
                Provide all relevant user information, nutritional targets, food logs, dietary preferences, restrictions, and specific objectives available in the current context.
                Clearly specify the requested operation and the expected outcome.

                Do not delegate unrelated tasks to this agent.

                Do not fabricate missing nutritional information. Clearly identify estimates, assumptions, and missing data.

                Return the PlannerAgent's results to the user or incorporate them into the overall response as appropriate.
                """
            ),
            "parameters": PlannerQuery.model_json_schema()
        }
    }
]

tool_specs_general = {
    "update_nutritional_context": {
        "function": Tools.update_nutritional_context,
        "params_model": NutritionalContextUpdate
    },
    "delegate_to_planner_agent": {
        "function": Tools.delegate_to_planner_agent,
        "params_model": PlannerQuery
    }
}

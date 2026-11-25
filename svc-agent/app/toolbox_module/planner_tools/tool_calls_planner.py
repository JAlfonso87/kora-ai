from app.toolbox_module.planner_tools.tool_functions_planner import PlannerTools
from app.toolbox_module.planner_tools.models.input_models_planner import (
    MealRegistrationInput,
    GoalArchtypeInput
)

tools_planner = [
    {
        "type": "function",
        "function": {
            "name": "register_new_meal",
            "description": (
                "Convierte la descripción de una comida compuesta dada por el usuario a sus ingredientes base y les asigna valores nutricionales"
            ),
            "parameters": MealRegistrationInput.model_json_schema(),
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_current_consumption",
            "description": (
                "Toma el contexto alimenticio actual y calcula los valores netos de calorías, proteína, carbohidratos y grasas actuales."
            ),
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_nutritional_requirements",
            "description": (
                "Toma el objetivo principal del plan nutricional del usuario y lo traduce a objetivos diarios de calorías, proteínas, "
                "grasas y carbohidratos."
            ),
            "parameters": GoalArchtypeInput.model_json_schema(),
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_remaining_nutrients",
            "description": (
                "Realiza las restas necesarias para estimar cuanto falta para alcanzar los objetivos diarios de nutrientes."
            ),
        },
    },
]

tool_specs_planner = {
    "register_new_meal": {
            "function": PlannerTools.register_new_meal,
            "params_model": MealRegistrationInput
    },
    "calculate_current_consumption": {
        "function": PlannerTools.calculate_current_consumption,
        "params_model": None
    },
    "calculate_nutritional_requirements": {
        "function": PlannerTools.calculate_nutritional_requirements,
        "params_model": GoalArchtypeInput
    },
    "calculate_remaining_nutrients": {
        "function": PlannerTools.calculate_remaining_nutrients,
        "params_model": None
    }
}

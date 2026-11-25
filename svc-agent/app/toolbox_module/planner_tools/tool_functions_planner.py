from langchain_core.messages import SystemMessage, HumanMessage

from app.ai_module.agents.structurer.structurer_agent import StructurerAgent

from app.context_module.nutritional_profile.models import NutritionalContext, Goals
from app.context_module.food_profile.models import FoodContext

from app.context_module.food_profile.models import Meal
from app.toolbox_module.planner_tools.models.input_models_planner import MealRegistrationInput, GoalArchtypeInput


class PlannerTools():
    def register_new_meal(nutritional_context: NutritionalContext, food_context: FoodContext, args: MealRegistrationInput) -> Meal:
        meal_translator = StructurerAgent(Meal)
        structured_meal = meal_translator.invoke([
            SystemMessage(content="""
                Toma la descripción de los alimentos del usuario y tradúcelo al esquema designado. Realiza las estimaciones
                necesarias para adaptar correctamente las cantidades a los esquemas de valores nutricionales.
            """),
            HumanMessage(content=f"""
                Descripción del alimento:
                {args.meal_description}
            """)
        ])

        payload = {
            "action": "REGISTERED_NEW_MEAL",
            "content": structured_meal.model_dump()
        }

        print(f"\nfunction: 'register_new_meal'")
        print(f"returning: {payload}")

        return payload

    def calculate_current_consumption(nutritional_context: NutritionalContext, food_context: FoodContext):
        calories_kcal: float = 0.0
        fats_g: float = 0.0
        protein_g: float = 0.0
        carbohydrates_g: float = 0.0

        for meal in food_context.meals:
            for food in meal.involved_foods:
                for ingredient in food.ingredients:
                    proportion = ingredient.quantity_g / 100
                    nutrients = ingredient.nutrients_per_100g

                    calories_kcal += nutrients.calories_kcal * proportion
                    fats_g += nutrients.fats_g * proportion
                    protein_g += nutrients.protein_g * proportion
                    carbohydrates_g += nutrients.carbohydrates_g * proportion

        payload = {
            "action": "CALCULATED_CURRENT_CONSUMPTION",
            "content": {
                "calories_kcal": calories_kcal, 
                "fats_g": fats_g, 
                "protein_g": protein_g, 
                "carbohydrates_g": carbohydrates_g
            }
        }

        print(f"\nfunction: 'calculate_current_consumption' ")
        print(f"returning: {payload}")

        return payload
                        
    def calculate_nutritional_requirements(nutritional_context: NutritionalContext, food_context: FoodContext, args: GoalArchtypeInput):
        goal_setter = StructurerAgent(Goals)
        goals = goal_setter.invoke([
            SystemMessage(content="""
                Toma el objetivo principal del plan, y asigna valores de objetivo diario de calorías, carbohidratos, proteínas y grasas.
            """),
            HumanMessage(content=f"""
                Objetivo principal del plan:
                {args.primary_goal}
            """)
        ])
        
        payload = {
            "action": "REGISTERED_NUTRITIONAL_GOALS",
            "content": goals.model_dump()
        }

        print(f"\nfunction: 'calculate_nutritional_requirements' ")
        print(f"returning: {payload}")

        return payload

    def calculate_remaining_nutrients(nutritional_context: NutritionalContext, food_context: FoodContext):
        targets = {
            "calorie_target_kcal": nutritional_context.goals.calorie_target_kcal,
            "protein_target_kcal": nutritional_context.goals.protein_target_g,
            "fat_target_kcal": nutritional_context.goals.fats_target_g,
            "carbohydrates_target_kcal": nutritional_context.goals.carbohydrates_target_g
        }

        current = {
            "calories_kcal": nutritional_context.current_consumption.calories_kcal,
            "protein_g": nutritional_context.current_consumption.protein_g,
            "fats_g": nutritional_context.current_consumption.fats_g,
            "carbohydrates_g": nutritional_context.current_consumption.carbohydrates_g
        }

        remaining = {
            "calories_kcal": targets["calorie_target_kcal"] - current["calories_kcal"],
            "protein_g": targets["protein_target_kcal"] - current["protein_g"],
            "fats_g": targets["fat_target_kcal"] - current["fats_g"],
            "carbohydrates_g": targets["carbohydrates_target_kcal"] - current["carbohydrates_g"]
        }


        payload = {
            "action": "CALCULATED_REMAINING_NUTRIENTS",
            "content": remaining
        }

        print(f"\nfunction: 'calculate_remaining_nutrients' ")
        print(f"returning: {payload}")

        return payload

    

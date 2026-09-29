from app.tools.tool_requirements import ProteinQueryRequirements, NutritionalContextUpdate
from app.nutritional_context.nutritional_context_models import NutritionalContext

class Tools():
    def update_nutritional_context(
        context: NutritionalContext,
        update: NutritionalContextUpdate,
    ) -> NutritionalContext:
        print("<< LLAMADA A LA FUNCIÓN 'update_context' >>")

        if context is None:
            context = NutritionalContext()

        if update.user_profile is not None:
            context.user_profile = update.user_profile

        if update.goals is not None:
            context.goals = update.goals

        if update.current_consumption is not None:
            context.current_consumption = update.current_consumption

        if update.food_preferences is not None:
            context.food_preferences = update.food_preferences

        if update.food_restrictions is not None:
            context.food_restrictions = update.food_restrictions

        return {
            "content": {
                "success": True,
            },
            "context": context
        }

    def protein_assistance_query(
        context: NutritionalContext,
        params: ProteinQueryRequirements
    ):
        print("<< LLAMADA A LA FUNCIÓN 'protein_assistance_query' >>")
        return {
            "content": {
                "success": True,
            },
            "context": context
        }
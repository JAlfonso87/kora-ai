from app.tools.tool_requirements import ProteinQueryRequirements, NutritionalContextUpdate,BayesReasoningRequirements
from app.context_module.nutritional_context_models import NutritionalContext
from typing import Any
from app.bayes import bayes_tool

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

    def bayes_reasoning_query(
        context: NutritionalContext | None,
        params: BayesReasoningRequirements,
        ) -> dict[str, Any]:
        """Run HU-012 Bayesian reasoning inside svc-agente (not a microservice)."""
        print("<< TOOL: bayes_reasoning >>")
        current_context = context or NutritionalContext()

        if hasattr(current_context, "model_dump"):
            context_data = current_context.model_dump(mode="python", exclude_none=True)
        elif hasattr(current_context, "dict"):
            context_data = current_context.dict(exclude_none=True)
        else:
            context_data = {}

        # Merge only the optional, scenario-specific signals supplied to the tool.
        # These must be grounded in the request/history/context, not guessed.
        if params.context:
            context_data.update(params.context)

        result = bayes_tool(
            scenario_id=params.scenario_id,
            evidence=params.evidence,
            context=context_data,
        )
        return {"content": result, "context": current_context}

from app.toolbox_module.general_tools.models.input_models_general import NutritionalContextUpdate, PlannerQuery, FoodContextUpdate
from app.context_module.nutritional_profile.models import NutritionalContext
from app.context_module.food_profile.models import FoodContext

from app.ai_module.agents.planner.planner_agent import PlannerAgent
from app.ai_module.agents.available_queries import PlannerAvailableQueries
from pydantic import BaseModel, Field

class SubAgentToolRequest(BaseModel):
    message: str = Field(
        description = "User's message that triggered the activation of the sub-agent."
    )
    contextual_messages: str = Field(
        description = "Brief list of previous messages before tool call to give simple context."
    )
    nutritional_context: str = Field(
        description = "User's nutritional context."
    )
    query: PlannerAvailableQueries = Field(
        description = "Simple instruction given by the main agent to the sub-agent."
    )

class SubAgentToolResponse(BaseModel):
    action: str = Field(
        description = "Action executed successfully by tool"
    ),
    content: dict = Field(
        description = "Final structured result from the sub-agent execution."
    )

class Tools():
    def update_nutritional_context(
        context: NutritionalContext,
        update: NutritionalContextUpdate,
        consumption_update: bool = False,
        goal_update: bool = False
    ) -> NutritionalContext:

        if context is None:
            context = NutritionalContext()

        if update.user_profile is not None:
            context.user_profile = update.user_profile

        if update.food_preferences is not None:
            context.food_preferences = update.food_preferences

        if update.food_restrictions is not None:
            context.food_restrictions = update.food_restrictions

        if goal_update is True:
            if update.goals is not None:
                context.goals = update.goals

            if update.remaining_nutrients is not None:
                context.remaining_nutrients = update.remaining_nutrients

        if consumption_update is True:
            if update.current_consumption is not None:
                context.current_consumption = update.current_consumption

        print(f"\nfunction: 'update_nutritional_context' ")
        print(f"returning: {context}")

        return context

    def update_food_context(
        context: FoodContext,
        update: FoodContextUpdate
    ) -> FoodContext:
        
        if context is None:
            context = FoodContext()

        if update.meals is not None:
            if context.meals is None:
                context.meals = []

            context.meals.extend(update.meals)

        print(f"\nfunction: 'update_food_context' ")
        print(f"returning: {context}")

        return context

    def delegate_to_planner_agent(planner_agent: PlannerAgent, nutritional_context: NutritionalContext, contextual_messages: list, args: PlannerQuery) -> list[SubAgentToolResponse]:
        tool_messages: list[SubAgentToolResponse] = []

        msg = planner_agent.model.invoke({
            "contextual_messages": contextual_messages,
            "context": nutritional_context,
            "query": args.query
        })

        if not msg.tool_calls:
            return tool_messages
        
        for tool_call in msg.tool_calls:
            result = SubAgentToolResponse(**planner_agent.tool_handler.handle(tool_call = tool_call))
            tool_messages.append(result)

        print(f"\nfunction: 'delegate_to_planner_agent' ")
        print(f"returning: {tool_messages}")
        
        return tool_messages
        

    

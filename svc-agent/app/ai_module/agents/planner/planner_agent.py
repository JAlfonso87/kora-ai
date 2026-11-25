from app.context_module.nutritional_profile.models import NutritionalContext
from app.context_module.food_profile.models import FoodContext

from app.ai_module.memory_manager.memory import Memory
from app.ai_module.agents.planner.preloader import PlannerModelPreloader

from app.toolbox_module.planner_tools.tool_handler_planner import ToolHandlerPlanner

class PlannerAgent:
    def __init__(self, session_id: str, nutritional_context: NutritionalContext | None, food_context: FoodContext | None):
        self.session_id = session_id
        self.model = PlannerModelPreloader().chain
        self.memory = Memory(session_id = self.session_id)
        self.nutritional_context = nutritional_context
        self.food_context = food_context
        self.tool_handler = ToolHandlerPlanner(nutritional_context = self.nutritional_context, food_context = self.food_context)



    
from app.context_module.nutritional_profile.models import NutritionalContext
from app.ai_module.agents.planner.prompt import SYSTEM_PROMPT

class PlannerAgent:
    def __init__(self, agent = None, context: NutritionalContext = None):
        self.agent = agent
        self.context = context

    def update(self, updated_context: NutritionalContext):
        self.context = updated_context

    
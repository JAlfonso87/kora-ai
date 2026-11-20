import os

from langchain_groq import ChatGroq
from app.context_module.nutritional_profile.models import NutritionalContext

from app.ai_module.agents.planner.prompt import SYSTEM_PROMPT
from app.ai_module.memory_manager.memory import Memory

class PlannerAgent:
    def __init__(self, session_id: str, context: NutritionalContext | None):
        self.session_id = session_id
        self.agent = ChatGroq(api_key=os.getenv("LLM_API_KEY"), model=os.getenv("LLM_MODEL"))
        self.memory = Memory(session_id = self.session_id)
        self.context = context



    
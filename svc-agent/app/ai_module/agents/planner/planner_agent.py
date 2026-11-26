from langchain.messages import SystemMessage

from app.context_module.nutritional_profile.models import NutritionalContext
from app.context_module.food_profile.models import FoodContext

from app.ai_module.memory_manager.memory import Memory
from app.ai_module.agents.planner.preloader import PlannerModelPreloader

from app.toolbox_module.planner_tools.tool_handler_planner import ToolHandlerPlanner
from app.inference_module.evaluators.rule_evaluator import RuleEngine

from app.toolbox_module.general_tools.models.output_models_general import SubAgentToolResponse

class PlannerAgent:
    def __init__(self, session_id: str, nutritional_context: NutritionalContext | None, food_context: FoodContext | None):
        self.session_id = session_id
        self.model = PlannerModelPreloader().chain
        self.memory = Memory(session_id = self.session_id)
        self.nutritional_context = nutritional_context
        self.food_context = food_context
        self.tool_handler = ToolHandlerPlanner(nutritional_context = self.nutritional_context, food_context = self.food_context)
        self.rule_engine = RuleEngine(self.session_id, self.nutritional_context, self.food_context)

    def invoke(self, args: dict):
        rule_messages: list[SystemMessage] = []
        tool_messages: list[SubAgentToolResponse] = []

        while True:
            payload = {
                "contextual_messages": args["contextual_messages"],
                "context": args["context"],
                "query": args["query"],
                "rule_messages": rule_messages
            }

            response = self.model.invoke(payload)

            if not response.tool_calls:
                return tool_messages
                    
            for tool_call in response.tool_calls:
                result = SubAgentToolResponse(**self.tool_handler.handle(tool_call = tool_call))
                rule_messages = self.rule_engine.get_evaluation_results()
                tool_messages.append(result)

            return tool_messages





    
from app.toolbox_module.general_tools.tool_pack_general import TOOLPACK_SPECS
from app.toolbox_module.bayes_tools.tool_functions_bayes import BayesTool
from app.ai_module.agents.planner.planner_agent import PlannerAgent
from app.context_module.nutritional_profile.models import NutritionalContext

class ToolHandler:
    def __init__(self, nutritional_context: NutritionalContext, planner_agent: PlannerAgent):
        self.nutritional_context = nutritional_context
        self.planner_agent = planner_agent
        
    def handle(self, tool_call: dict, contextual_messages: list):
        # Get the tool name and arguments from the LLM response.

        print(f"EXECUTING GENERAL TOOL '{tool_call["name"]}' WITH ARGUMENTS: {[tool_call["args"]]}")

        tool_name = tool_call["name"]
        arguments = tool_call["args"]

        payload = {
            "content": None,
            "context": self.nutritional_context
        }

        # Get the tool specification.
        tool = TOOLPACK_SPECS[tool_name]

        # Validate the arguments using the corresponding Pydantic model.
        params = tool["params_model"] if not arguments else tool["params_model"].model_validate(arguments)

        match tool_name:
            case "rag_query": 
                return tool["function"](params.query)
            case "bayes_reasoning":
                result = BayesTool.bayes_reasoning_query(self.nutritional_context, params)
            case "delegate_to_planner_agent":
                result = tool["function"](self.planner_agent, self.nutritional_context, contextual_messages, params)
            case _:
                result = tool["function"](self.nutritional_context, params) if params is not None else tool["function"](self.nutritional_context)
        
        payload["content"] = result

        # Return the standard response structure.
        #if isinstance(result, dict) and "content" in result and "context" in result:
        #    return result

        print(f"\nfunction: 'general_handler' ")
        print(f"returning: {payload}")
        
        return payload
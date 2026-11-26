from app.context_module.nutritional_profile.models import NutritionalContext
from app.context_module.food_profile.models import FoodContext

from app.toolbox_module.planner_tools.tool_pack_planner import TOOLPACK_SPECS_PLANNER

class ToolHandlerPlanner:
    def __init__(self, nutritional_context: NutritionalContext, food_context: FoodContext):
        self.nutritional_context = nutritional_context
        self.food_context = food_context

    def handle(self, tool_call: dict):
        print(f"(PLANNER TOOL HANDLER): EXECUTING PLANNER TOOL '{tool_call["name"]}' WITH ARGUMENTS: {[tool_call["args"]]}")

        tool_name = tool_call["name"]
        arguments = tool_call["args"]

        tool = TOOLPACK_SPECS_PLANNER[tool_name]
        params = tool["params_model"] if not arguments else tool["params_model"].model_validate(arguments)

        result = tool["function"](self.nutritional_context, self.food_context, params) if params is not None else tool["function"](self.nutritional_context, self.food_context)

        print(f"\nfunction: 'planner_handler' ")
        print(f"returning: {result}")

        return result




import json
from app.tools.tool_calls import tool_specs as tools

def handle_tool_call(tool_call, context):
    tool = tools[tool_call.function.name]
    # Intercepts Groq's tool call and transforms the argument list into a dictionary that is subject to be compared with an existent 'RequirementModel'
    arguments = json.loads(tool_call.function.arguments)

    # Validates the transformed argument dictionary against a 'RequirementModel' previously defined.
    params = tool["params_model"].model_validate(arguments)

    # Executes the function referred inside the dict entry selected with the just-validated set of params (see tool_calls.toool_specs for more info)
    # then returns the results of said function
    return tool["function"](context, params)
from app.tools.tool_calls import tool_specs as tools

def handle_tool_call(tool_call: dict, context):
    # Retrieves the requested tool name and its already-parsed arguments
    # from the LangChain tool call structure.
    tool_name = tool_call["name"]
    arguments = tool_call["args"]

    # Retrieves the corresponding tool specification using the tool name
    # requested by the LLM.
    tool = tools[tool_name]

    # Validates the tool arguments against the Pydantic requirements model
    # defined for the selected tool.
    params = tool["params_model"].model_validate(arguments)

    # Executes the corresponding tool function using the current nutritional
    # context and the validated parameters, then returns its result.
    return tool["function"](context, params)

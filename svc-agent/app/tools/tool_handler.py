from app.tools.tool_calls import tool_specs
from app.tools.tool_functions import Tools


def handle_tool_call(tool_call: dict, context):
    # Get the tool name and arguments from the LLM response.
    tool_name = tool_call["name"]
    arguments = tool_call["args"]

    # Get the tool specification.
    tool = tool_specs[tool_name]

    # Validate the arguments using the corresponding Pydantic model.
    params = tool["params_model"].model_validate(arguments)

    # Execute the requested tool.
    if tool_name == "bayes_reasoning":
        result = Tools.bayes_reasoning_query(
            context=context,
            params=params
        )
    else:
        result = tool["function"](context, params)

    # Return the standard response structure.
    if isinstance(result, dict) and "content" in result and "context" in result:
        return result

    return {
        "content": result,
        "context": context
    }
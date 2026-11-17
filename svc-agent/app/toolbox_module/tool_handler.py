from app.toolbox_module import TOOLPACK_SPECS
from app.toolbox_module.bayes_tools.tool_functions_bayes import BayesTool

def handle_tool_call(tool_call: dict, context):
    # Get the tool name and arguments from the LLM response.
    tool_name = tool_call["name"]
    arguments = tool_call["args"]

    # Get the tool specification.
    tool = TOOLPACK_SPECS[tool_name]

    # Validate the arguments using the corresponding Pydantic model.
    if not arguments:
        params = tool["params_model"]
    else:
        params = tool["params_model"].model_validate(arguments)

    # Execute the requested tool.
    if tool_name == "bayes_reasoning":
        result = BayesTool.bayes_reasoning_query(
            context=context,
            params=params
        )
    else:
        if params is not None:
            result = tool["function"](context, params)
        else:
            result = tool["function"](context)

    # Return the standard response structure.
    if isinstance(result, dict) and "content" in result and "context" in result:
        return result

    return {
        "content": result,
        "context": context
    }
    # Execute RAG independently from nutritional-context tools.
    if tool_name == "rag_query":
        return tool["function"](params.query)

    # Executes the corresponding tool function using the current nutritional
    # context and the validated parameters, then returns its result.
    return tool["function"](context, params)

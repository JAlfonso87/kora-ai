from app.toolbox_module.bayes_tools.tool_calls_bayes import tools_probabilistic, tool_specs_probabilistic
from app.toolbox_module.vision_tools.tool_calls_vision import tools_vision, tool_specs_vision
from app.toolbox_module.general_tools.tool_calls_general import tools_general, tool_specs_general

TOOLPACK = (
    tools_general
    + tools_vision
    + tools_probabilistic
)

TOOLPACK_SPECS = tool_specs_general | tool_specs_vision | tool_specs_probabilistic
from .rag_tools.tool_calls_rag import tools_rag
from .rag_tools.tool_calls_rag import tool_specs_rag

from .bayes_tools.tool_calls_bayes import tools_probabilistic
from .bayes_tools.tool_calls_bayes import tool_specs_probabilistic

from .vision_tools.tool_calls_vision import tools_vision
from .vision_tools.tool_calls_vision import tool_specs_vision

from .general_tools.tool_calls_general import tools_general
from .general_tools.tool_calls_general import tool_specs_general

TOOLPACK = (
    tools_general
    + tools_vision
    + tools_probabilistic
    + tools_rag
)

TOOLPACK_SPECS = tool_specs_general | tool_specs_vision | tool_specs_probabilistic | tool_specs_rag
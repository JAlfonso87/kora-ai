from app.toolbox_module.planner_tools.tool_calls_planner import tools_planner, tool_specs_planner
from app.toolbox_module.rag_tools.tool_calls_rag import tools_rag, tool_specs_rag

TOOLPACK_PLANNER = (
    tools_planner +
    tools_rag
)

TOOLPACK_SPECS_PLANNER = tool_specs_planner | tool_specs_rag

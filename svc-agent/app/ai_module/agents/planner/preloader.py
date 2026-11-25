import os

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.ai_module.agents.planner.prompt import SYSTEM_PROMPT
from app.toolbox_module.planner_tools.tool_pack_planner import TOOLPACK_PLANNER

PROMPT_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="contextual_messages"),
        ("system", "El NutritionalContext actual es: {context}"),
        ("human", "Tienes la siguiente instrucción: {query}")
    ]
)
class PlannerModelPreloader:
    def __init__(self):
        self.provider = ChatGroq(api_key=os.getenv("LLM_API_KEY"), model=os.getenv("LLM_MODEL"))
        self.provider_w_tools = self.provider.bind_tools(TOOLPACK_PLANNER)
        self.template = PROMPT_TEMPLATE
        self.chain = self.template | self.provider_w_tools
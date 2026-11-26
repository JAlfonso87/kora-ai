import os

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.ai_module.agents.general.prompt import SYSTEM_PROMPT, RAG_SYSTEM_PROMPT

from app.toolbox_module.general_tools.tool_pack_general import TOOLPACK

PROMPT_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("system", "Current nutritional context:\n{nutritional_context}"),
        ("system", RAG_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{message}"),
        MessagesPlaceholder(variable_name="tool_messages"),
    ]
)

class ModelPreloader:
    def __init__(self):
        self.provider = ChatGroq(api_key=os.getenv("LLM_API_KEY"), model=os.getenv("LLM_MODEL"))
        self.provider_w_tools = self.provider.bind_tools(TOOLPACK)
        self.template = PROMPT_TEMPLATE
        self.chain = self.template | self.provider_w_tools
        

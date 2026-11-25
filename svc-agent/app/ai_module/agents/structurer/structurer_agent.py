import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import BaseModel

load_dotenv()

class StructurerAgent:
    def __init__(self, structure: type[BaseModel]):
        self.structure = structure
        self.provider = ChatGroq(api_key = os.getenv("LLM_API_KEY"), model = os.getenv("LLM_MODEL"))
        self.structurer = self.provider.with_structured_output(self.structure)

    def invoke(self, messages: list):
        return self.structurer.invoke(messages)

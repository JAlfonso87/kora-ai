from dotenv import load_dotenv
from pathlib import Path
import json

from langchain_core.messages import ToolMessage

from app.ai_module.memory_manager.memory import Memory
from app.ai_module.agents.general.preloader import ModelPreloader

from app.toolbox_module.tool_handler import handle_tool_call

from app.context_module.nutritional_profile.manager import ContextManager
from app.context_module.nutritional_profile.models import NutritionalContext
from app.context_module.nutritional_profile.enforcer import context_enforcer

from app.inference_module.generators.fact_generator import build_fact_base
from app.inference_module.evaluators.rule_evaluator import RuleEngine
from app.toolbox_module.tool_input_models import Rule
from app.inference_module.formatters.debug_formatter import format_evaluation
from app.inference_module.formatters.rule_message_formatter import evaluation_to_message

# Loads environment variables from the local .env file.
load_dotenv()

class GeneralAgent:
    def __init__(self, memory: Memory = None, session_id: str | None = None):
        self.session_id = session_id
        self.model = ModelPreloader().chain
        self.memory = memory
        self.context_manager = ContextManager()
        self.rule_engine = RuleEngine()

    @property
    def context(self) -> NutritionalContext:
        if self.session_id is not None:
            return self.context_manager.get_context(self.session_id)
    
    def generate_response(
        self,
        message: str,
    ) -> tuple[str, str, dict | None]:
        """
        Generates an LLM response using conversation memory,
        nutritional context, and available tools.

        Returns:
            A tuple containing the LLM response and the session ID used.
        """

        facts = build_fact_base(self.context)
        # print("<< LISTA DE HECHOS RECUPERADOS >>")
        # print(facts)

        # Stores the current user message.
        self.memory.add_message("user", message)

        # Initializes the messages used during tool execution.
        tool_messages = []
        # Initializes the mesages generated during rule evaluation.
        rule_messages = []

        # Stores the last result returned by the vision tool.
        last_vision_result = None

        while True:

            context_enforcer(self.context_manager, self.session_id, self.memory.get_last_messages())

            # Generates the LLM response using the current context,
            # conversation history, and tool execution history.
            msg = self.model.invoke(
                {
                    "message": message,
                    "nutritional_context": self.context,
                    "history": self.memory.get_history(),
                    "tool_messages": tool_messages,
                    "rule_messages": rule_messages
                }
            )

            print("AGENT:", msg.content)

            # Returns the final response when the LLM does not request any tools.
            if not msg.tool_calls:
                assistant_content = msg.content or ""
                self.memory.add_message("assistant", assistant_content)
                return assistant_content, last_vision_result

            # Stores the AI message containing the requested tool calls
            # so their results can be linked back to the original calls.
            tool_messages.append(msg)

            # Executes every tool requested by the LLM.
            for tool_call in msg.tool_calls:

                # Executes the requested application tool using
                # the current nutritional context.
                result = handle_tool_call(
                    tool_call = tool_call,
                    context = self.context
                )
                
                # Captures the result returned by the vision tool.
                if tool_call["name"] == "load_and_analyze_picture":

                    vision_content = (
                        result.get("content")
                        if isinstance(result, dict)
                        else result
                    )

                    if isinstance(vision_content, dict) and "status" in vision_content:
                        last_vision_result = vision_content

                print(" << RESULT RECUPERADO >> ")
                print(result)

                # RAG retrieves knowledge without modifying nutritional context.
                if tool_call["name"] == "rag_query":
                    tool_content = result

                else:
                    # Saves the nutritional context returned by the tool.
                    self.context_manager.save_context(
                        session_id = self.session_id,
                        context = result["context"]
                    )

                    # Transforms the freshly retrieved NutritionalContext into a list of facts that will be subject to rules.
                    facts = build_fact_base(result["context"])

                    RULES_PATH = (
                        Path(__file__).resolve().parent.parent
                        / "inference_module"
                        / "rules_catalog.json"
                    )

                    with open(RULES_PATH, "r", encoding="utf-8") as file:
                        rules_data = json.load(file)

                    rules = [
                        Rule.model_validate(data)
                        for data in rules_data["rules"]
                    ]

                    rules_result = self.rule_engine.evaluate(facts, rules)

                    # Preserves only rule_messages related to the current tool_execution
                    rule_messages = [evaluation_to_message(rules_result)]

                    tool_content = result["content"]

                # Sends the tool result back to the LLM and associates it
                # with the corresponding tool call through its ID.
                tool_messages.append(
                    ToolMessage(
                        content=json.dumps(
                            tool_content,
                            ensure_ascii=False
                        ),
                        tool_call_id=tool_call["id"]
                    )
                )

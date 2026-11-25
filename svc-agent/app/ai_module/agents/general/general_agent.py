from dotenv import load_dotenv
from pathlib import Path
import json
import uuid

from langchain_core.messages import ToolMessage

from app.ai_module.memory_manager.memory import Memory
from app.ai_module.agents.general.preloader import ModelPreloader

from app.context_module.nutritional_profile.manager import NutritionalContextManager
from app.context_module.nutritional_profile.enforcer import context_enforcer

from app.context_module.food_profile.manager import FoodContextManager
from app.context_module.food_profile.enforcer import food_context_enforcer

from app.inference_module.generators.fact_generator import build_fact_base
from app.inference_module.evaluators.rule_evaluator import RuleEngine
from app.toolbox_module.general_tools.models.input_models_general import Rule
from app.inference_module.formatters.debug_formatter import format_evaluation
from app.inference_module.formatters.rule_message_formatter import evaluation_to_message

from app.ai_module.agents.planner.planner_agent import PlannerAgent
from app.toolbox_module.general_tools.tool_handler_general import ToolHandler

# Loads environment variables from the local .env file.
load_dotenv()

class GeneralAgent:
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.model = ModelPreloader().chain
        self.memory = Memory(self.session_id)

        self.nutritional_context_manager = NutritionalContextManager()
        self.nutritional_context = self.nutritional_context_manager.get_context(self.session_id)

        self.food_context_manager = FoodContextManager()
        self.food_context = self.food_context_manager.get_context(self.session_id)

        self.tool_handler = ToolHandler(self.nutritional_context, PlannerAgent(self.session_id, self.nutritional_context, self.food_context))
        self.rule_engine = RuleEngine()
    
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

        facts = build_fact_base(self.nutritional_context)
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

            context_enforcer(self.nutritional_context_manager, self.session_id, self.memory.get_last_messages())
            print("CURRENT CONTEXTS: ")
            print("NUTRITIONAL CONTEXT: ")
            print(self.nutritional_context)
            print("FOOD CONTEXT: ")
            print(self.food_context)

            # Generates the LLM response using the current context,
            # conversation history, and tool execution history.

            msg = self.model.invoke({
                "message": message,
                "nutritional_context": self.nutritional_context,
                "history": self.memory.get_history(),
                "tool_messages": tool_messages,
                "rule_messages": rule_messages
            })
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
                result = self.tool_handler.handle(tool_call = tool_call, contextual_messages = self.memory.get_last_messages())

                if tool_call["name"] == "delegate_to_planner_agent":
                    for message in result["content"]:
                        tool_messages.append(
                            ToolMessage(
                                content=json.dumps(
                                    message.model_dump(),
                                    ensure_ascii=False
                                ),
                                tool_call_id=tool_call["id"]
                            )
                        )
                        match message.action:
                            case "REGISTERED_NEW_MEAL":
                                food_context_enforcer(self.food_context_manager, self.session_id, [message.model_dump()])
                            case "CALCULATED_CURRENT_CONSUMPTION":
                                context_enforcer(self.nutritional_context_manager, self.session_id, [message.model_dump()], consumption_update = True)
                            case "REGISTERED_NUTRITIONAL_GOALS" | "CALCULATE_REMAINING_NUTRIENTS":
                                context_enforcer(self.nutritional_context_manager, self.session_id, [message.model_dump()], goal_update = True)

                    continue

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
                    self.nutritional_context_manager.save_context(
                        session_id = self.session_id,
                        context = self.nutritional_context
                    )

                    # Transforms the freshly retrieved NutritionalContext into a list of facts that will be subject to rules.
                    facts = build_fact_base(result["context"])

                    RULES_PATH = (
                        Path(__file__).resolve().parent.parent.parent.parent
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

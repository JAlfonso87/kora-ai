from dotenv import load_dotenv
from pathlib import Path
import json
import os
import uuid


from langchain_groq import ChatGroq
from langchain_core.messages import ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.ai_module.memory_manager.memory import get_history, add_message, get_last_messages
from app.ai_module.prompt_manager.prompts import SYSTEM_PROMPT, RAG_SYSTEM_PROMPT

from app.toolbox_module import TOOLPACK
from app.toolbox_module.tool_handler import handle_tool_call

from app.context_module.nutritional_profile.manager import get_context, save_context
from app.context_module.nutritional_profile.models import NutritionalContext
from app.context_module.nutritional_profile.enforcer import context_enforcer

from app.inference_module.generators.fact_generator import build_fact_base
from app.inference_module.evaluators.rule_evaluator import RuleEngine
from app.toolbox_module.tool_input_models import Rule
from app.inference_module.formatters.debug_formatter import format_evaluation
from app.inference_module.formatters.rule_message_formatter import evaluation_to_message

# Loads environment variables from the local .env file.
load_dotenv()


# Initializes the LLM using the configured API key and model.
llm = ChatGroq(
    api_key=os.getenv("LLM_API_KEY"),
    model=os.getenv("LLM_MODEL"),
)

rule_engine = RuleEngine()

# Makes the available application tools accessible to the LLM.
llm_with_tools = llm.bind_tools(TOOLPACK)

# Builds the conversation prompt using the system instructions,
# nutritional context, previous history, current user message,
# and messages generated during tool execution.
PROMPT_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("system", "Current nutritional context:\n{nutritional_context}"),
        ("system", RAG_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{message}"),
        MessagesPlaceholder(variable_name="tool_messages"),
        MessagesPlaceholder("rule_messages", optional=True),
    ]
)

# Creates the LangChain execution pipeline using the prompt template
# and the LLM with tool-calling support enabled.
chain = PROMPT_TEMPLATE | llm_with_tools


def generate_response(
    message: str,
    session_id: str | None = None,
    nutritional_context: NutritionalContext | None = None,
) -> tuple[str, str, dict | None]:
    """
    Generates an LLM response using conversation memory,
    nutritional context, and available tools.

    Returns:
        A tuple containing the LLM response and the session ID used.
    """

    if not session_id:
        session_id = str(uuid.uuid4())

    # Retrieves the current context for this session.
    current_context = get_context(session_id)
    print("<< CURRENT NUTRITIONAL CONTEXT >>")
    print(current_context.model_dump())

    # Updates the context only when new context is received.
    if nutritional_context is not None:

        # Preserves consumption data already stored in the session.
        if nutritional_context.current_consumption is None:
            nutritional_context.current_consumption = (
                current_context.current_consumption
            )

        if nutritional_context.remaining_nutrients is None:
            nutritional_context.remaining_nutrients = (
                current_context.remaining_nutrients
            )

        save_context(
            session_id=session_id,
            context=nutritional_context,
        )

        facts = build_fact_base(nutritional_context)
        print("<< LISTA DE HECHOS RECUPERADOS >>")
        print(facts)

    # Retrieves the conversation history.
    history = get_history(session_id)

    # Stores the current user message.
    add_message(session_id, "user", message)

    # Initializes the messages used during tool execution.
    tool_messages = []
    # Initializes the mesages generated during rule evaluation.
    rule_messages = []

    # Stores the last result returned by the vision tool.
    last_vision_result = None

    while True:

        # Retrieves the latest nutritional context on every iteration,
        # allowing tool-generated updates to be used immediately.
        context = get_context(session_id)

        context_msg = context_enforcer(session_id, get_last_messages(session_id))
        print(context_msg)

        # Generates the LLM response using the current context,
        # conversation history, and tool execution history.
        msg = chain.invoke(
            {
                "message": message,
                "nutritional_context": context,
                "history": history,
                "tool_messages": tool_messages,
                "rule_messages": rule_messages
            }
        )

        print("TOOL CALLS:", msg.tool_calls)
        print("LLM RESPONSE:", msg.content)

        # Returns the final response when the LLM does not request any tools.
        if not msg.tool_calls:
            assistant_content = msg.content or ""
            add_message(session_id, "assistant", assistant_content)
            return assistant_content, session_id, last_vision_result

        # Stores the AI message containing the requested tool calls
        # so their results can be linked back to the original calls.
        tool_messages.append(msg)

        # Executes every tool requested by the LLM.
        for tool_call in msg.tool_calls:
            context = get_context(session_id)

            # Executes the requested application tool using
            # the current nutritional context.
            result = handle_tool_call(
                tool_call=tool_call,
                context=context
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
                print(" << GUARDANDO CONTEXTO >> ")
                save_context(
                    session_id=session_id,
                    context=result["context"]
                )
                print(" << CONTEXTO GUARDADO >> ")

                # Transforms the freshly retrieved NutritionalContext into a list of facts that will be subject to rules.
                facts = build_fact_base(result["context"])
                print("<< LISTA DE HECHOS RECUPERADOS >>")
                print(facts)

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

                rules_result = rule_engine.evaluate(facts, rules)

                """print("<< REGLAS EVALUADAS: >>")
                print(format_evaluation(rules_result, color=False, show_all=False))"""

                # Preserves only rule_messages related to the current tool_execution
                rule_messages = [evaluation_to_message(rules_result)]
                """print("<< REGLAS EVALUADAS: >>")
                print(rule_messages)"""

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

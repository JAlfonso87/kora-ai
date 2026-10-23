from dotenv import load_dotenv
from pathlib import Path
import json, os, uuid


from langchain_groq import ChatGroq
from langchain_core.messages import ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.services.memory import get_history, add_message
from app.tools.tool_calls import groq_tools
from app.tools.tool_handler import handle_tool_call
from app.context_module.nutritional_context_management import get_context, save_context
from app.context_module.nutritional_context_models import NutritionalContext

from app.inference_engine.fact_generator import build_fact_base
from app.inference_engine.rule_evaluator import RuleEngine
from app.inference_engine.required_models import Rule
from app.inference_engine.debug_formatter import format_evaluation
from app.inference_engine.rule_message_formatter import evaluation_to_message

# Loads environment variables from the local .env file.
load_dotenv()


# Initializes the LLM using the configured API key and model.
llm = ChatGroq(
    api_key=os.getenv("LLM_API_KEY"),
    model=os.getenv("LLM_MODEL")
)

rule_engine = RuleEngine()

# Makes the available application tools accessible to the LLM.
llm_with_tools = llm.bind_tools(groq_tools)

# Defines the base behavior and restrictions of Kora AI.
SYSTEM_PROMPT = """
You are Kora AI, an assistant specialized in nutrition.

GENERAL RULES:
- Use only information available in the user request,
  conversation history, and nutritional context.
- Never invent missing information.
- Do not provide medical diagnoses or complete diet plans.

TOOL USAGE:
- When the user asks about their protein requirements,
  protein intake, remaining protein needs, or personalized
  protein recommendations, call protein_assistance_query.
- Before calling protein_assistance_query, ensure that
  update_nutritional_context has processed any new nutritional
  information explicitly provided in the current user message.
- If the current message contains new or updated nutritional
  information, call update_nutritional_context before responding.
- Do not claim to have performed a nutritional calculation
  unless the required tool has actually been executed.
- If essential information is missing, explain what is missing
  instead of inventing values.

RESPONSE:
- Provide a clear and relevant answer.
- Respect the available nutritional context and safety restrictions.
"""

# Builds the conversation prompt using the system instructions,
# nutritional context, previous history, current user message,
# and messages generated during tool execution.
PROMPT_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("system", "Current nutritional context:\n{nutritional_context}"),
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
) -> tuple[str, str]:
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
    print(current_context)

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

    while True:

        # Retrieves the latest nutritional context on every iteration,
        # allowing tool-generated updates to be used immediately.
        context = get_context(session_id)

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
            print(" << LLAMADA DIRECTA >>")
            assistant_content = msg.content or ""
            add_message(session_id, "assistant", assistant_content)
            return assistant_content, session_id

        # Stores the AI message containing the requested tool calls
        # so their results can be linked back to the original calls.
        tool_messages.append(msg)

        # Executes every tool requested by the LLM.
        for tool_call in msg.tool_calls:
            print(" << RECUPERANDO CONTEXTO >> ")
            context = get_context(session_id)
            print(" << CONTEXTO RECUPERADO >> ")

            # Executes the requested application tool using
            # the current nutritional context.
            result = handle_tool_call(
                tool_call=tool_call,
                context=context
            )

            print(" << RESULT RECUPERADO >> ")
            print(result)

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
            RULES_PATH = (Path(__file__).resolve().parent.parent / "inference_engine" / "rules_catalog.json")

            with open(RULES_PATH, "r", encoding="utf-8") as file:
                rules_data = json.load(file)

            rules = [
                Rule.model_validate(data)
                for data in rules_data["rules"]
            ]

            rules_result = rule_engine.evaluate(facts, rules)
            #print("<< REGLAS EVALUADAS: >>")
            #print(format_evaluation(rules_result, color=False, show_all=False))

            # Preserves only rule_messages related to the current tool_execution
            rule_messages = [evaluation_to_message(rules_result)]
            print("<< REGLAS EVALUADAS: >>")
            print(rule_messages)

            # Sends the tool result back to the LLM and associates it
            # with the corresponding tool call through its ID.
            tool_messages.append(
                ToolMessage(
                    content=json.dumps(
                        result["content"],
                        ensure_ascii=False
                    ),
                    tool_call_id=tool_call["id"]
                )
            )

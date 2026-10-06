from dotenv import load_dotenv
import json
import os
import uuid

from langchain_groq import ChatGroq
from langchain_core.messages import ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.services.memory import get_history, add_message
from app.tools.tool_calls import groq_tools
from app.tools.tool_handler import handle_tool_call
from app.nutritional_context.nutritional_context_management import (
    get_context,
    save_context,
)


# Loads environment variables from the local .env file.
load_dotenv()


# Initializes the LLM using the configured API key and model.
llm = ChatGroq(
    api_key=os.getenv("LLM_API_KEY"),
    model=os.getenv("LLM_MODEL")
)

# Makes the available application tools accessible to the LLM.
llm_with_tools = llm.bind_tools(groq_tools)


# Defines the base behavior and restrictions of Kora AI.
SYSTEM_PROMPT = (
    "You are Kora AI, an assistant specialized in nutrition. "
    "Analyze the user's request using the nutritional context provided when available. "
    "Use only the information available in the request, conversation history, and nutritional context. "
    "Do not invent or assume information that has not been provided. "
    "Generate a clear, relevant, and concise response based on the available context. "
    "Do not provide medical diagnoses or complete diet plans."
)


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
    ]
)


# Creates the LangChain execution pipeline using the prompt template
# and the LLM with tool-calling support enabled.
chain = PROMPT_TEMPLATE | llm_with_tools


def generate_response(
    message: str,
    session_id: str | None = None,
) -> tuple[str, str]:
    """
    Generates an LLM response using conversation memory,
    nutritional context, and available tools.

    Returns:
        A tuple containing the LLM response and the session ID used.
    """

    # Creates a new session when the request does not provide one.
    if not session_id:
        session_id = str(uuid.uuid4())

    # Retrieves only the conversation history that existed
    # before the current user message.
    history = get_history(session_id)

    # Stores the current user message for future requests.
    add_message(session_id, "user", message)

    # Stores AI tool calls and their corresponding results
    # only for the current request execution.
    tool_messages = []

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
                "tool_messages": tool_messages
            }
        )

        # Returns the final response when the LLM does not request any tools.
        if not msg.tool_calls:
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
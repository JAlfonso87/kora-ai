
import requests

from django.db import transaction

from management.models import User, Conversation, Message
from management.services.agent_client import call_agent
from management.services.nutritional_context_service import (
    build_nutritional_context,
)

def create_conversation(user_id, title):
    user = User.objects.get(id=user_id)

    return Conversation.objects.create(
        user=user,
        title=title,
    )


def send_conversation_message(
    user_id,
    conversation_id,
    message_text,
):

    conversation = Conversation.objects.get(
        id=conversation_id,
        user_id=user_id,
    )


    user_message = Message.objects.create(
        conversation=conversation,
        role="user",
        content=message_text,
    )



    nutritional_context = build_nutritional_context(
        conversation.user
    )

    agent_result = call_agent(
        message=message_text,
        session_id=str(conversation.id),
        nutritional_context=nutritional_context,
    )

    if not isinstance(agent_result, dict):
        raise ValueError("La respuesta del agente no es válida.")

    agent_text = agent_result.get("response")

    if not isinstance(agent_text, str) or not agent_text.strip():
        raise ValueError("El agente no devolvió una respuesta válida.")


    with transaction.atomic():
        assistant_message = Message.objects.create(
            conversation=conversation,
            role="assistant",
            content=agent_text.strip(),
        )

        conversation.save(update_fields=["updated_at"])

    return user_message, assistant_message


def get_conversation_history(user_id, conversation_id):
    conversation = Conversation.objects.get(
        id=conversation_id,
        user_id=user_id,
    )

    messages = conversation.messages.order_by(
        "created_at",
        "id",
    )

    return conversation, messages


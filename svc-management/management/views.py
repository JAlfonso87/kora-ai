
import requests

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.fields import UUIDField
from rest_framework.response import Response

from management.models import User, Conversation
from management.serializers import (
    ConversationCreateSerializer,
    MessageCreateSerializer,
    MessageSerializer,
    ConversationHistorySerializer,
)
from management.services.agent_client import call_agent
from management.services.conversation_service import (
    create_conversation,
    send_conversation_message,
    get_conversation_history,
)


@api_view(["POST"])
def agent_test(request):
    message = request.data.get("message")

    if not isinstance(message, str) or not message.strip():
        return Response(
            {"error": "El mensaje es obligatorio."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        result = call_agent(message.strip())
    except requests.RequestException:
        return Response(
            {"error": "No fue posible comunicarse con el agente."},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    return Response({"agent_response": result})


@api_view(["POST"])
def create_conversation_view(request):
    serializer = ConversationCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        conversation = create_conversation(
            user_id=serializer.validated_data["user_id"],
            title=serializer.validated_data["title"],
        )
    except User.DoesNotExist:
        return Response(
            {"error": "El usuario no existe."},
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response(
        ConversationHistorySerializer(conversation).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
def send_message_view(request, conversation_id):
    serializer = MessageCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        user_message, assistant_message = send_conversation_message(
            user_id=serializer.validated_data["user_id"],
            conversation_id=conversation_id,
            message_text=serializer.validated_data["message"],
        )
    except Conversation.DoesNotExist:
        return Response(
            {"error": "La conversación no existe o no pertenece al usuario."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except requests.RequestException:
        return Response(
            {
                "error": "No fue posible comunicarse con el agente.",
                "user_message_saved": True,
            },
            status=status.HTTP_502_BAD_GATEWAY,
        )
    except ValueError as exc:
        return Response(
            {"error": str(exc)},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    return Response(
        {
            "conversation_id": str(conversation_id),
            "user_message": MessageSerializer(user_message).data,
            "assistant_message": MessageSerializer(
                assistant_message
            ).data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
def conversation_history_view(request, conversation_id):
    user_id = request.query_params.get("user_id")

    if not user_id:
        return Response(
            {"error": "El parámetro user_id es obligatorio."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user_id = UUIDField().run_validation(user_id)
    except ValidationError as exc:
        return Response(
            {"error": exc.detail},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        conversation, messages = get_conversation_history(
            user_id=user_id,
            conversation_id=conversation_id,
        )
    except Conversation.DoesNotExist:
        return Response(
            {"error": "La conversación no existe o no pertenece al usuario."},
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response(
        {
            "conversation": ConversationHistorySerializer(
                conversation
            ).data,
            "messages": MessageSerializer(messages, many=True).data,
        },
        status=status.HTTP_200_OK,
    )
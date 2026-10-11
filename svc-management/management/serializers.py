
from rest_framework import serializers

from management.models import Conversation, Message


class ConversationCreateSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    title = serializers.CharField(
        max_length=255,
        required=False,
        default="Nueva conversación",
    )


class MessageCreateSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    message = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
    )

    def validate_message(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "El mensaje no puede estar vacío."
            )

        return value.strip()


class ConversationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ["id", "title", "created_at", "updated_at"]


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "role", "content", "created_at"]
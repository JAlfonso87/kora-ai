
from django.urls import path

from management import views

urlpatterns = [
    path(
        "agent-test/",
        views.agent_test,
        name="agent_test",
    ),
    path(
        "conversations/",
        views.create_conversation_view,
        name="create_conversation",
    ),
    path(
        "conversations/<uuid:conversation_id>/messages/",
        views.send_message_view,
        name="send_message",
    ),
    path(
        "conversations/<uuid:conversation_id>/history/",
        views.conversation_history_view,
        name="conversation_history",
    ),
]
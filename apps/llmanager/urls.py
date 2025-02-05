from django.urls import path
from . import views

urlpatterns = [
    path("prompt/", views.ChatbotPromptView.as_view(), name="get_chatbot_prompts"),
    path(
        "conversation/<int:conversation_id>/", views.ChatbotPromptView.as_view(), name="read-update-delete-conversation"
    ),
    path("conversation/", views.ConversationView.as_view(), name="list-create-conversation"),
    path("agents/", views.AgentViewSet.as_view({"get": "list"}), name="list-agents"),
]

from django.urls import path
from . import views

urlpatterns = [
    path('prompt/', views.ChatbotPromptView.as_view(), name='get_chatbot_prompts'),
]
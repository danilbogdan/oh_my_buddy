from django.urls import path
from apps.telegrambot.views import WebhookView

urlpatterns = [
    path('webhook/<int:user_id>/<int:bot_id>/', WebhookView.as_view(), name='webhook'),
]

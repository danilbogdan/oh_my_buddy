from django.contrib.auth.models import User
from django.db import models


class TelegramBot(models.Model):
    token = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="telegram_bots")
    agent = models.ForeignKey("llmanager.Agent", null=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)
    webhook_url = models.URLField(max_length=255, help_text="URL where Telegram will send updates for this bot")

    def __str__(self):
        return self.name


class ConversationMessage(models.Model):
    conversation = models.ForeignKey("Conversation", on_delete=models.CASCADE, related_name="messages")
    message = models.TextField()
    author = models.CharField(null=True, blank=True, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation from {self.author} on {self.created_at}"


class Conversation(models.Model):
    bot = models.ForeignKey(TelegramBot, on_delete=models.CASCADE, related_name="conversations")
    chat_id = models.IntegerField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation in chat {self.chat_id} on {self.created_at}"

from django.contrib.auth.models import User
from django.db import models
from telegram.constants import ParseMode


class TelegramBot(models.Model):
    token = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="telegram_bots")
    agent = models.ForeignKey("llmanager.Agent", null=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)
    webhook_url = models.URLField(max_length=255, help_text="URL where Telegram will send updates for this bot")
    log_conversation = models.BooleanField(default=True)
    description = models.TextField(blank=True, max_length=512, help_text="Bot description shown in Telegram")
    short_description = models.CharField(max_length=120, blank=True, help_text="Short description for bot profile")
    bot_specific_prompt = models.TextField(
        blank=True, help_text="Prompt which will be added to extend agent prompt to be more user-specific"
    )
    redirect_media_chat_id = models.CharField(
        max_length=50, blank=True, null=True, help_text="Chat ID where media messages will be redirected"
    )
    """
    class ParseMode(StringEnum):
        This enum contains the available parse modes. The enum
        members of this enumeration are instances of :class:`str` and can be treated as such.

        .. versionadded:: 20.0
        

        __slots__ = ()

        MARKDOWN = "Markdown"
        obj:`str`: Markdown parse mode.

        Note:
            :attr:`MARKDOWN` is a legacy mode, retained by Telegram for backward compatibility.
            You should use :attr:`MARKDOWN_V2` instead.
        
        MARKDOWN_V2 = "MarkdownV2"
        obj:`str`: Markdown parse mode version 2
        HTML = "HTML"
        obj:`str`: HTML parse mode
    """
    parse_mode = models.CharField(
        max_length=50,
        choices=[(tag.value, tag.value) for tag in ParseMode] + [(None, "None")],
        null=True,
        blank=True,
        default=ParseMode.HTML.value,
    )

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
    chat_id = models.CharField(max_length=50, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation in chat {self.chat_id} on {self.created_at}"


class Lead(models.Model):
    service_name = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=50,
        default="new",
    )
    notes = models.TextField()

    def __str__(self):
        return f"{self.username} {self.email} {self.phone_number}"

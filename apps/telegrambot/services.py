import json
import logging
from typing import TYPE_CHECKING, Union

import requests
from telegram import Update, constants
from telegram.ext import Application

from .models import Conversation, ConversationMessage, TelegramBot

if TYPE_CHECKING:
    from django.http import HttpRequest


logger = logging.getLogger("django")


def build_webhook_url(request: "HttpRequest", bot: "TelegramBot"):
    return request.build_absolute_uri(f"/telegrambot/webhook/{bot.user_id}/{bot.id}/").replace("http://", "https://")


def register_webhook(bot_token: str, webhook_url: str):
    url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    response = requests.post(url, data={"url": webhook_url})
    return response.json()


def send_message(chat_id: int, bot_token: str, message: str):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    response = requests.post(url, json=payload)
    return response.json()


async def log_conversation(bot_id: int, chat_id: Union[str, int], message: str, author: str):
    conversation, _ = await Conversation.objects.aget_or_create(chat_id=int(chat_id), bot_id=bot_id)
    await ConversationMessage.objects.acreate(conversation=conversation, message=message, author=author)


async def parse_update(body, token):
    application = Application.builder().token(token).build()
    logger.info(body)
    update = Update.de_json(json.loads(body), application.bot)
    await application.bot.send_chat_action(chat_id=update.message.chat.id, action=constants.ChatAction.TYPING)
    return update

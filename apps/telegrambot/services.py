import json
from typing import TYPE_CHECKING
from django.utils import timezone
import requests
from telegram import Update
from telegram.ext import Application
from .models import TelegramBot

if TYPE_CHECKING:
    from django.http import HttpRequest


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


def log_conversation(chat_id: int, message: str):
    # Placeholder for logging conversation to the database
    # This function can be expanded to save messages to a model
    print(f"User {chat_id}: {message} at {timezone.now()}")


async def parse_update(body, token):
    application = Application.builder().token(token).build()
    update = Update.de_json(json.loads(body), application.bot)
    return update

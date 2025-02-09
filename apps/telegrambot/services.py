import json
from typing import TYPE_CHECKING

import requests
from telegram import Update, constants
from telegram.ext import Application

from aimanager.tools.scheme import llm_tool

from .models import Conversation, ConversationMessage, Lead, TelegramBot

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


async def log_conversation(bot: TelegramBot, chat_id: str, author: str, message: str):
    conversation, _ = await Conversation.objects.aget_or_create(chat_id=str(chat_id), bot_id=bot.id)
    if bot.log_conversation:
        await ConversationMessage.objects.acreate(conversation=conversation, message=message, author=author)


async def parse_update(body, token):
    application = Application.builder().token(token).build()
    update = Update.de_json(json.loads(body), application.bot)
    await application.bot.send_chat_action(chat_id=update.message.chat.id, action=constants.ChatAction.TYPING)
    return update


@llm_tool
async def create_lead(service_name: str, email: str, phone_number: str, notes: str, status: str) -> None:
    """
    Creates a lead record in the CRM system based on a conversation in chat.
    Args:
        service_name (str): The name of the service for which the lead is being created. Fill this field according to provided service and user interest
        email (str): The email address of the lead. Ask user to provide it. If not provided - set null
        phone_number (str): The phone number of the lead. Ask user to provide it. If not provided - set null
        notes (str): Additional notes about the lead. You should deside by your own what to put here
        status (str): The status of the lead. One of: 'New', 'Contacted', 'Qualified', 'Lost'. You should deside which to set. If user ready to go further - set Qualified. If user rejects - set Lost. If need contact - leave New.
    Returns:
        None
    """
    await Lead.objects.acreate(
        service_name=service_name,
        email=email,
        phone_number=phone_number,
        notes=notes,
        status=status,
    )
    return "Lead created in CRM"


def update_bot_properties(bot: TelegramBot):
    """Update Telegram bot properties using Telegram Bot API"""
    base_url = f"https://api.telegram.org/bot{bot.token}"

    # Update bot commands
    # requests.post(
    #     f"{base_url}/setMyCommands",
    #     json={
    #         "commands": [
    #             {"command": "start", "description": "Start the bot"},
    #             {"command": "help", "description": "Show help message"},
    #         ]
    #     },
    # )
    # Update bot description and about
    if bot.description:
        requests.post(f"{base_url}/setMyDescription", json={"description": bot.description})
    if bot.short_description:
        requests.post(f"{base_url}/setMyShortDescription", json={"short_description": bot.short_description})
    if bot.name:
        requests.post(f"{base_url}/setMyName", json={"name": bot.name})

    return True

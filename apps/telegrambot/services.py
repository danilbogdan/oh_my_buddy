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


@llm_tool
async def notify_manager(service_name: str, email: str, phone_number: str, notes: str, status: str) -> None:
    """
    This function is responsible for alerting the manager when a client is ready to proceed with a service. It triggers a notification based on the client's interest and the service provided. This function ensures that the manager is immediately informed when a client expresses readiness for a deal or when the type of service.
    Args:
        service_name (str): The name of the service for which the notification is being created. Fill this field according to provided service and user interest.
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
    return "Manager successfully notified"


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


@llm_tool
async def list_pandadoc_files(
    count: int = 10,
    order_by: str = "name",
    order_direction: str = "asc",
    name_pattern: str = None,
    file_extension: str = None
) -> str:
    """
    Lists files in the /tmp/pandadoc/ directory with various filtering options.
    Args:
        count (int): Maximum number of files to return. Default is 10.
        order_by (str): Field to order by. One of: 'name', 'size', 'modified'. Default is 'name'.
        order_direction (str): Order direction. One of: 'asc', 'desc'. Default is 'asc'.
        name_pattern (str): Pattern to match in file names. If None, no pattern matching is applied.
        file_extension (str): Filter by file extension (e.g., 'pdf', 'docx'). If None, all extensions are included.
    Returns:
        str: JSON string containing the list of files with their properties
    """
    import os
    from datetime import datetime
    import re

    base_path = "/tmp/pandadoc/"
    if not os.path.exists(base_path):
        return "[]"

    files = []
    for filename in os.listdir(base_path):
        if file_extension and not filename.endswith(f".{file_extension}"):
            continue
        if name_pattern and not re.search(name_pattern, filename, re.IGNORECASE):
            continue

        file_path = os.path.join(base_path, filename)
        if os.path.isfile(file_path):
            stat = os.stat(file_path)
            files.append({
                "name": filename,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "extension": os.path.splitext(filename)[1][1:]
            })

    # Sort files
    reverse = order_direction.lower() == "desc"
    files.sort(key=lambda x: x[order_by], reverse=reverse)

    # Limit count
    files = files[:count]

    return json.dumps(files)


@llm_tool
async def rename_pandadoc_file(existing_name: str, new_name: str) -> str:
    """
    Renames a file in the /tmp/pandadoc/ directory.
    Args:
        existing_name (str): Current name of the file
        new_name (str): New name for the file
    Returns:
        str: Success or error message
    """
    import os
    import shutil

    base_path = "/tmp/pandadoc/"
    old_path = os.path.join(base_path, existing_name)
    new_path = os.path.join(base_path, new_name)

    if not os.path.exists(old_path):
        return f"Error: File '{existing_name}' does not exist"
    
    if os.path.exists(new_path):
        return f"Error: File '{new_name}' already exists"

    try:
        shutil.move(old_path, new_path)
        return f"Successfully renamed '{existing_name}' to '{new_name}'"
    except Exception as e:
        return f"Error renaming file: {str(e)}"

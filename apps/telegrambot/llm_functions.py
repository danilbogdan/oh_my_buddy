from telegram.ext import Application

from aimanager.tools.scheme import llm_tool
from apps.telegrambot.models import Lead
from apps.telegrambot.tools.carousel_generator import generate_carousel


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
    This function is responsible for alerting the manager when a client is ready to proceed with a service. It triggers a notification based on the client’s interest and the service provided. This function ensures that the manager is immediately informed when a client expresses readiness for a deal or when the type of service.
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


@llm_tool
async def generate_carousel_from_text(text: str, entities: dict = None, token: str = None, chat_id: str = None):
    """
    This function generates Instagram carousel images from the provided text and sends them to a specified Telegram chat. It utilizes the Telegram bot API to send the generated images as photos to the chat.
    Args:
        text (str): Required: The text from which to generate the Instagram carousel images.
        token (str): Not Required: will be provided manually by application. The token for the Telegram bot to authenticate the API requests.
        chat_id (str): Not Required: will be provided manually by application. The chat ID of the Telegram chat where the images will be sent.
    Returns:
        None
    """
    application = Application.builder().token(token).build()
    images = generate_carousel(text, entities=entities, return_buffer=True)
    for image in images:
        image.seek(0)
        await application.bot.send_photo(chat_id=chat_id, photo=image)

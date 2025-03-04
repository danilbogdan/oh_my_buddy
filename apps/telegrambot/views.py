import logging

from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from telegram import constants
from telegram import error as tgerror

from aimanager.agent.builder import AsyncLLMAgentBuilder
from apps.llmanager.repositories.agent import AgentRepository
from apps.telegrambot.models import TelegramBot
from apps.telegrambot.services import create_lead, log_conversation, notify_manager, parse_update

logger = logging.getLogger("django")


@method_decorator(csrf_exempt, name="dispatch")
class WebhookView(View):
    # TODO: use secret token to verify bot auth https://core.telegram.org/bots/api#setwebhook
    # TODO: possibly, use python telegram bot queue or process_update
    # https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#custom-solution
    async def post(self, request, bot_id, user_id):
        try:
            await handle_update(request, bot_id, user_id)
        except Exception as e:
            logger.error(f"Error processing update: {str(e)}", exc_info=e)
        finally:
            return JsonResponse({"status": "ok"})

    def http_method_not_allowed(self, request, *args, **kwargs):
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)


async def handle_update(request: HttpRequest, bot_id: int, user_id: int) -> None:
    bot_model = await TelegramBot.objects.aget(id=bot_id)
    update = await parse_update(request.body, bot_model.token)
    await log_conversation(bot_model, update.message.chat.id, update.message.chat.username, update.message.text)
    model, provider, instructions = await AgentRepository.async_get_agent_params(bot_model.agent_id)
    instructions += f"\n {bot_model.bot_specific_prompt}"
    agent = AsyncLLMAgentBuilder.build(agent_name="base", provider=provider, model=model, system_prompt=instructions)
    agent.register_tool(create_lead)
    agent.register_tool(notify_manager)
    response = await agent.async_generate_response(update.message.text, update.message.chat.id, bot_model.id)
    await log_conversation(bot_model, update.message.chat.id, bot_model.name, response)
    try:
        await update.message.reply_text(response, parse_mode=constants.ParseMode.HTML)
    except tgerror.BadRequest:
        logger.info("Cant parse as HTML, try simple response...")
        await update.message.reply_text(response)

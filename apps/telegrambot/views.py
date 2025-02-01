import json
import logging
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from telegram import Update

from aimanager.agent.builder import AsyncLLMAgentBuilder
from apps.llmanager.repositories.agent import AgentRepository
from apps.telegrambot.models import TelegramBot
from apps.telegrambot.services import log_conversation, parse_update

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class WebhookView(View):
    # TODO: use secret token to verify bot auth https://core.telegram.org/bots/api#setwebhook
    # TODO: possibly, use python telegram bot queue or process_update
    # https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#custom-solution
    async def post(self, request, bot_id, user_id):
        try:
            bot_model = await TelegramBot.objects.aget(id=bot_id)
            update = await parse_update(request.body, bot_model.token)
            # await log_conversation(update.message.text, bot_id, user_id)
            model, provider, instructions = await AgentRepository.async_get_agent_params(bot_model.agent_id)
            agent = AsyncLLMAgentBuilder.build(
                agent_name="base", provider=provider, model=model, system_prompt=instructions
            )
            response = await agent.async_generate_response(update.message.text, user_id, update.message.chat.id)
            # await log_conversation(response, bot_id, user_id)
            await update.message.reply_text(response)
            return JsonResponse({"status": "ok"})
        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=200)
        except Exception as e:
            logger.error(f"Error processing update: {str(e)}", exc_info=e)
            return JsonResponse({"status": "error", "message": str(e)}, status=200)

    def http_method_not_allowed(self, request, *args, **kwargs):
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)


# async def handle_update(update: Update, bot_id: int, user_id: int):
#     """
#     write simple telegram echo handler
#     """
#     log_conversation(bot_id, user_id)
#     await update.message.reply_text(f'Hello {update.effective_user.first_name}')

import logging
from django.conf import settings
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from apps.llmanager.providers import LLMProviderFactory
from apps.llmanager.repositories.provider_config import ProviderConfigRepository
from apps.llmanager.providers._openai import OpenAIProvider

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize LLM provider
provider = ProviderConfigRepository.get_provider()
llm_provider = LLMProviderFactory.get_llm_provider(provider)

# Initialize OpenAI provider
openai_provider = OpenAIProvider()
openai_provider.init_client()

# Storage for threads
threads = {}


# Define a few command handlers. These usually take the two arguments update and context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued and create a thread."""
    user = update.effective_user
    chat_id = update.message.chat_id

    # Create a thread
    thread = openai_provider.create_thread()
    threads[chat_id] = thread.id

    await update.message.reply_html(
        rf"Hi {user.mention_html()}! Your conversation thread has been created.",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the user message and get response from LLM provider."""
    user_message = update.message.text
    chat_id = update.message.chat_id

    # Add message to the thread
    thread_id = threads.get(chat_id)
    if not thread_id:
        await update.message.reply_text("Please start a conversation first by using /start.")
        return

    openai_provider.create_message(thread_id=thread_id, role="user", content=user_message)

    # Run the assistant on the thread
    openai_provider.create_run_and_poll(assistant_id=openai_provider.assistant_id, thread_id=thread_id)

    # Send the response back to the user
    await update.message.reply_text(openai_provider.get_latest_message_text(thread_id))


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - handle the message with LLM provider
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

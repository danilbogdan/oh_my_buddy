from django.core.management.base import BaseCommand
from apps.telegrambot.bot import main


class Command(BaseCommand):
    help = "Start the Telegram bot"

    def handle(self, *args, **kwargs):
        main()

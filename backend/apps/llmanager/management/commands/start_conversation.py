from typing import TYPE_CHECKING
from django.core.management.base import BaseCommand
from apps.llmanager.providers import LLMProviderFactory
from apps.llmanager.repositories.provider_config import ProviderConfigRepository


class Command(BaseCommand):
    help = "Start a conversation with the LLM"

    def handle(self, *args, **kwargs):
        provider = ProviderConfigRepository.get_provider()
        llm_provider = LLMProviderFactory.get_llm_provider(provider)

        self.stdout.write(self.style.SUCCESS(f"Starting conversation with LLM '{llm_provider.name}' ..."))

        while True:
            prompt = input("You: ")
            if prompt.lower() in ["exit", "quit"]:
                self.stdout.write(self.style.SUCCESS("Conversation ended."))
                break
            response = llm_provider.generate_response(prompt)
            self.stdout.write(f"LLM: {response}")

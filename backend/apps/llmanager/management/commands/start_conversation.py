from django.core.management.base import BaseCommand
from apps.llmanager.providers import LLMFactory
from apps.llmanager.repositories.provider_config import ProviderConfigRepository


class Command(BaseCommand):
    help = "Start a conversation with the LLM"

    def handle(self, *args, **kwargs):
        provider_name = ProviderConfigRepository.get_provider()
        llm_provider = LLMFactory.get_llm_provider(provider_name)

        self.stdout.write(self.style.SUCCESS("Starting conversation with LLM..."))

        while True:
            prompt = input("You: ")
            if prompt.lower() in ["exit", "quit"]:
                self.stdout.write(self.style.SUCCESS("Conversation ended."))
                break
            response = llm_provider.generate_response(prompt)
            self.stdout.write(f"LLM: {response}")

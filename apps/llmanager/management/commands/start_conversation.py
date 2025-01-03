from django.core.management.base import BaseCommand
from aimanager.agent.builder import LLMAgentBuilder


class Command(BaseCommand):
    help = "Start a conversation with the LLM"

    def handle(self, *args, **kwargs):
        agent = LLMAgentBuilder.build(agent_name="base", provider="openrouter")

        self.stdout.write(self.style.SUCCESS(f"Starting conversation with LLM '{agent.name}' ..."))
        name = input("Enter your name: ")
        while True:
            prompt = input("You: ")
            if prompt.lower() in ["exit", "quit"]:
                self.stdout.write(self.style.SUCCESS("Conversation ended."))
                break
            if prompt == "history":
                conversation = agent.get_conversation(name)
                for message in conversation:
                    self.stdout.write(f"{message['role']}: {message['content']}")
                continue
            response = agent.generate_response(prompt, user_id=name)
            self.stdout.write(f"LLM: {response}")

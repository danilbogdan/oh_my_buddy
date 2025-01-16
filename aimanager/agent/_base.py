import os
import logging
from typing import Generator

from django.conf import settings
from ._interface import AIAgentInterface
from aimanager.memory.builder import MemoryProviderBuilder
from aimanager.completions.builder import CompletionsClientBuilder

logger = logging.getLogger('django')


class BaseAgent(AIAgentInterface):
    name = "base"
    model_provider = os.getenv("DEFAULT_MODEL_PROVIDER", "openai")
    memory_provider = os.getenv("DEFAULT_MEMORY_PROVIDER", "redis")
    system_prompt = (
        "You are an AI assistant. The assistant is helpful, creative,"
        "clever, and very friendly. You help users with his tasks and answers his questions."
        "The assistant is very good at understanding context and subtext. The assistant is "
        "very good at understanding natural language."
    )

    def init_agent(self, *args, **kwargs) -> dict:
        self.memory = MemoryProviderBuilder.build(self.memory_provider)
        self.completions = CompletionsClientBuilder.build(kwargs.get('provider') or self.model_provider)
        self.model = kwargs.get('model')

    def get_conversation(self, user_id: str, conversation_id: str = None) -> list[dict]:
        conversation = self.memory.get_conversation(user_id, self.name, conversation_id)
        return conversation or []

    def clear_conversation(self, user_id: str, conversation_id: str = None) -> bool:
        return self.memory.delete_conversation(user_id, self.name, conversation_id)

    def generate_response(self, prompt: str, user_id: str, conversation_id: str = None) -> str:
        system_messages = [{"role": "system", "content": self.system_prompt}]
        messages = self.get_conversation(user_id, conversation_id)
        user_message = [{"role": "user", "content": prompt}]
        self.memory.add_messages_to_conversation(user_message, user_id, self.name, conversation_id)
        response = self.completions.generate_response(system_messages + messages + user_message, model=self.model)
        message = [{"role": "assistant", "content": response}]
        self.memory.add_messages_to_conversation(message, user_id, self.name, conversation_id)
        return response

    def generate_response_stream(self, prompt: str, user_id: str, conversation_id: str = None) -> Generator[str]:
        system_messages = [{"role": "system", "content": self.system_prompt}]
        messages = self.get_conversation(user_id, conversation_id)
        user_message = [{"role": "user", "content": prompt}]
        self.memory.add_messages_to_conversation(user_message, user_id, self.name, conversation_id)
        stream = self.completions.generate_response(system_messages + messages + user_message, model=self.model, stream=True)
        response = ""
        for chunk in stream:
            yield chunk
            response += chunk
        message = [{"role": "assistant", "content": response}]
        self.memory.add_messages_to_conversation(message, user_id, self.name, conversation_id)
        return response

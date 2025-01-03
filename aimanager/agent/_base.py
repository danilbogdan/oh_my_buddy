from ._interface import AIAgentInterface
from aimanager.memory.builder import MemoryProviderBuilder
from aimanager.completions.builder import CompletionsClientBuilder


class BaseAgent(AIAgentInterface):
    name = "base"
    model_provider = "openai"
    memory_provider = "redis"
    system_prompt = (
        "You are an AI assistant. The assistant is helpful, creative,"
        "clever, and very friendly. You help users with his tasks and answers his questions."
        "The assistant is very good at understanding context and subtext. The assistant is "
        "very good at understanding natural language."
    )

    def init_agent(self, *args, **kwargs) -> dict:
        self.memory = MemoryProviderBuilder.build(self.memory_provider)
        self.completions = CompletionsClientBuilder.build(kwargs.get('provider') or self.model_provider)

    def get_conversation(self, user_id: str, system: bool = True) -> list[dict]:
        conversation = self.memory.get_conversation(user_id, self.name)
        if not system:
            conversation = [message for message in conversation if message["role"] != "system"]
        return conversation

    def clear_conversation(self, user_id: str) -> dict:
        return self.memory.delete_conversation(user_id, self.name)

    def generate_response(self, prompt: str, user_id: str) -> str:
        messages = self.get_conversation(user_id)
        if not messages:
            messages = [{"role": "system", "content": self.system_prompt}]
        messages.append({"role": "user", "content": prompt})
        response = self.completions.generate_response(messages)
        messages.append({"role": "assistant", "content": response})
        self.memory.save_conversation(messages, user_id, self.name)
        return response

    def generate_response_stream(self, prompt: str, user_id: str) -> str:
        messages = self.get_conversation(user_id)
        if not messages:
            messages = [{"role": "system", "content": self.system_prompt}]
        messages.append({"role": "user", "content": prompt})
        stream = self.completions.generate_response(messages, stream=True)
        response = ""
        for chunk in stream:
            yield chunk
            response += chunk
        messages.append({"role": "assistant", "content": response})
        self.memory.save_conversation(messages, user_id, self.name)
        return response

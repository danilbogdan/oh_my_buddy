from django.conf import settings
from openai import OpenAI

from ._interface import LLMProviderInterface
from apps.llmanager.repositories.provider_config import ProviderConfigRepository


class LMStudioProvider(LLMProviderInterface):
    name = "lmstudio"

    def __init__(self):
        self.client = OpenAI(base_url=f"{settings.CUSTOM_OPENAI_HOST}:{settings.CUSTOM_OPENAI_PORT}/v1", api_key="lm-studio")
        self.model = ProviderConfigRepository.get_model()
        self.system_instruction = ProviderConfigRepository.get_system_instruction()
        self._messages = []
        self._messages.append({"role": "system", "content": self.system_instruction})

    def generate_response(self, prompt: str) -> str:

        self._messages.append({"role": "user", "content": prompt})
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self._messages,
        )
        reply = response.choices[0].message.content
        self._messages.append({"role": "assistant", "content": reply})
        return reply

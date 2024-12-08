from ._openai import OpenAIProvider
from ._interface import LLMProviderInterface


class LLMFactory:
    @staticmethod
    def get_llm_provider(provider_name: str) -> LLMProviderInterface:
        if provider_name == "openai":
            return OpenAIProvider()
        else:
            raise ValueError(f"Unknown provider: {provider_name}")

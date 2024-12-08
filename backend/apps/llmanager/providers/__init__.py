from ._lmstudio import *
from ._openai import *
from ._interface import LLMProviderInterface


class LLMProviderFactory:
    @staticmethod
    def get_llm_provider(provider_name: str) -> LLMProviderInterface:
        for provider in LLMProviderInterface.__subclasses__():
            if provider.name == provider_name:
                return provider()
        raise ValueError(f"Unknown provider: {provider_name}")
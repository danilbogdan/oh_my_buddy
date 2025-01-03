from .lmstudio import LMStudioProvider
from .openai import OpenAIProvider
from .custom_openai_api_provider import CustomOpenAIApiProvider
from .openrouter import OpenRouterProvider
from ._interface import CompletionProviderInterface


class CompletionsClientBuilder:
    @staticmethod
    def build(provider_name: str) -> CompletionProviderInterface:
        for provider in [OpenAIProvider, LMStudioProvider, OpenRouterProvider, CustomOpenAIApiProvider]:
            if provider.name == provider_name:
                return provider()
        raise ValueError(f"Unknown provider: {provider_name}")

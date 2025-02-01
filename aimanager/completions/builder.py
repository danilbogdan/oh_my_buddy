from .lmstudio import LMStudioProvider
from .openai import OpenAIProvider, AsyncOpenAIProvider
from .custom_openai_api_provider import CustomOpenAIApiProvider, AsyncCustomOpenAIApiProvider
from .openrouter import OpenRouterProvider
from ._interface import AsyncCompletionProviderInterface, CompletionProviderInterface


class CompletionsClientBuilder:
    @staticmethod
    def build(provider_name: str) -> CompletionProviderInterface:
        for provider in [OpenAIProvider, LMStudioProvider, OpenRouterProvider, CustomOpenAIApiProvider]:
            if provider.name == provider_name:
                return provider()
        raise ValueError(f"Unknown provider: {provider_name}")


class AsyncCompletionsClientBuilder:
    @staticmethod
    def build(provider_name: str) -> AsyncCompletionProviderInterface:
        for provider in [AsyncOpenAIProvider, AsyncCustomOpenAIApiProvider]:
            if provider.name == provider_name:
                return provider()
        return AsyncOpenAIProvider()

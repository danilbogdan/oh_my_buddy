import os

from .custom_openai_api_provider import CustomOpenAIApiProvider


class OpenRouterProvider(CustomOpenAIApiProvider):
    name = "openrouter"
    model = os.getenv("OPENROUTER_MODEL") or "google/gemini-2.0-flash-exp:free"
    api_key = os.getenv("OPENROUTER_API_KEY")
    host = "https://openrouter.ai/api"
    port = None

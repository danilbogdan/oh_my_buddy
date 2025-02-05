import os

from .custom_openai_api_provider import CustomOpenAIApiProvider


class LMStudioProvider(CustomOpenAIApiProvider):
    name = "lmstudio"
    model = "gpt-4o-mini"
    api_key = "lm-studio"
    host = os.getenv("LLM_STUDIO_HOST") or "localhost"
    port = os.getenv("LLM_STUDIO_PORT") or 5000

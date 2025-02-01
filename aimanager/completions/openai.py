import os
import backoff
from openai import AsyncOpenAI, OpenAI

from .custom_openai_api_provider import CustomOpenAIApiProvider, AsyncCustomOpenAIApiProvider


class OpenAIProvider(CustomOpenAIApiProvider):
    name = "openai"
    model = "gpt-4o-mini"

    def init_client(self, *args, **kwargs):
        self.client = OpenAI(api_key=os.getenv("API_KEY"))


class AsyncOpenAIProvider(AsyncCustomOpenAIApiProvider):
    name = "openai"
    model = "gpt-4o-mini"

    def init_client(self, *args, **kwargs):
        self.client = lambda: AsyncOpenAI(api_key=os.getenv("API_KEY"))

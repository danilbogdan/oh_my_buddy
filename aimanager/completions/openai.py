import os
import backoff
from openai import OpenAI

from .custom_openai_api_provider import CustomOpenAIApiProvider


class OpenAIProvider(CustomOpenAIApiProvider):
    name = "openai"
    model = "gpt-4o-mini"

    def init_client(self, *args, **kwargs):
        self.client = OpenAI(api_key=os.getenv("API_KEY"))

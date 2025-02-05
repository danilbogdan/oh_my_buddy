import os
from typing import AsyncGenerator, Generator, Union
import backoff
from openai import OpenAI, AsyncOpenAI

from ._interface import CompletionProviderInterface, AsyncCompletionProviderInterface


class CustomOpenAIApiProvider(CompletionProviderInterface):
    name = "custom"
    model = os.getenv("CUSTOM_OPENAI_MODEL") or "gpt-4o-mini"
    host = os.getenv("CUSTOM_OPENAI_HOST") or "localhost"
    port = os.getenv("CUSTOM_OPENAI_PORT") or 5000
    api_key = os.getenv("CUSTOM_OPENAI_API_KEY") or None

    def init_client(self, *args, **kwargs):
        host = kwargs.get("host") or self.host
        port = kwargs.get("port") or self.port
        api_key = kwargs.get("api_key") or self.api_key
        if port:
            base_url = f"{host}:{port}/v1"
        else:
            base_url = f"{host}/v1"
        self.client = OpenAI(base_url=base_url, api_key=api_key)

    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    def generate_response(
        self, messages: list = None, model: str = None, stream: bool = False
    ) -> Union[str, Generator]:
        response = self.client.chat.completions.create(model=model or self.model, messages=messages, stream=stream)
        if not stream:
            return response.choices[0].message.content
        else:
            for chunk in response:
                content = chunk.choices[0].delta.content
                if content is not None:
                    yield content


class AsyncCustomOpenAIApiProvider(AsyncCompletionProviderInterface):
    name = "custom"
    model = os.getenv("CUSTOM_OPENAI_MODEL") or "gpt-4o-mini"
    host = os.getenv("CUSTOM_OPENAI_HOST") or "localhost"
    port = os.getenv("CUSTOM_OPENAI_PORT") or 5000
    api_key = os.getenv("CUSTOM_OPENAI_API_KEY") or None

    def init_client(self, *args, **kwargs):
        host = kwargs.get("host") or self.host
        port = kwargs.get("port") or self.port
        api_key = kwargs.get("api_key") or self.api_key
        if port:
            base_url = f"{host}:{port}/v1"
        else:
            base_url = f"{host}/v1"
        self.client = lambda: AsyncOpenAI(base_url=base_url, api_key=api_key)

    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def async_generate_response(self, messages: list = None, model: str = None, stream: bool = False) -> str:
        async with self.client() as c:
            response = await c.chat.completions.create(model=model or self.model, messages=messages, stream=stream)
            return response.choices[0].message.content

    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def async_generate_response_stream(
        self, messages: list = None, model: str = None, stream: bool = False
    ) -> AsyncGenerator:
        async with self.client() as c:
            response = await c.chat.completions.create(model=model or self.model, messages=messages, stream=stream)
            async for chunk in response:
                content = chunk.choices[0].delta.content
                if content is not None:
                    yield content

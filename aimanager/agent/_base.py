import asyncio
import inspect
import json
import logging
import os
from typing import AsyncGenerator, Generator, Union

from aimanager.completions.builder import AsyncCompletionsClientBuilder, CompletionsClientBuilder
from aimanager.memory.builder import AsyncMemoryProviderBuilder, MemoryProviderBuilder
from aimanager.tools import invoker, prompts

from ._interface import AIAgentInterface, AsyncAIAgentInterface

logger = logging.getLogger("django")


class BaseAgent(AIAgentInterface):
    name = "base"
    model_provider = os.getenv("DEFAULT_MODEL_PROVIDER", "openai")
    memory_provider = os.getenv("DEFAULT_MEMORY_PROVIDER", "redis")
    tools = None
    system_prompt = (
        "You are an AI assistant. The assistant is helpful, creative,"
        "clever, and very friendly. You help users with his tasks and answers his questions."
        "The assistant is very good at understanding context and subtext. The assistant is "
        "very good at understanding natural language."
    )

    def _compose_messages_list(
        self, prompt: str, user_id: Union[str, int], conversation_id: Union[str, int]
    ) -> list[dict]:
        instruction = self.system_prompt
        if self.tools_registry:
            instruction += f"\n{prompts.FUNCTION_INSTRUCTION}"
            schemes = [tool.llm_schema for tool in self.tools_registry.values()]
            instruction += f"\n{json.dumps(schemes)}"

        system_messages = [{"role": "system", "content": instruction}]
        conversation_history = self.get_conversation(user_id, conversation_id)
        user_message = [{"role": "user", "content": prompt}]
        self.memory.add_messages_to_conversation(user_message, user_id, self.name, conversation_id)
        return system_messages + conversation_history + user_message

    def _check_tools(self, response: str, conversation_list: list) -> dict:
        response = invoker.parse_llm_response(response)
        message = []
        while response["type"] == "function":
            result = invoker.trigger_function(response, self.tools_registry)
            fname = response["name"]
            try:
                if inspect.iscoroutine(result):
                    result = asyncio.run(result)
                message += [
                    {
                        "role": "developer",
                        "content": f"You successfully triggered a function {fname} and it returned: {result}. Please use this result in your response.",
                    }
                ]
            except Exception as e:
                message += [
                    {
                        "role": "developer",
                        "content": f"You tried to trigger function {fname} but excepthion was rised: {e}",
                    }
                ]
            response = self.completions.generate_response(conversation_list + message, model=self.model)
            response = invoker.parse_llm_response(response)
        return response["content"]

    def register_tool(self, tool):
        if not hasattr(tool, "llm_schema"):
            raise TypeError(f"Cant register tool {tool.__name__}: no scheme")
        self.tools_registry[tool.__name__] = tool

    def init_agent(self, *args, **kwargs) -> dict:
        self.memory = MemoryProviderBuilder.build(self.memory_provider)
        self.completions = CompletionsClientBuilder.build(kwargs.get("provider") or self.model_provider)
        self.system_prompt = kwargs.get("system_prompt") or self.system_prompt
        self.model = kwargs.get("model")
        self.tools_registry = {}
        for tool in kwargs.get("tools") or self.tools or []:
            self.register_tool(tool)

    def get_conversation(self, user_id: str, conversation_id: str = None) -> list[dict]:
        conversation = self.memory.get_conversation(user_id, self.name, conversation_id)
        return conversation or []

    def clear_conversation(self, user_id: str, conversation_id: str = None) -> bool:
        return self.memory.delete_conversation(user_id, self.name, conversation_id)

    def generate_response(self, prompt: str, user_id: str, conversation_id: str = None) -> str:
        messages = self._compose_messages_list(prompt, user_id, conversation_id)
        response = self.completions.generate_response(messages, model=self.model)
        tools_response = self._check_tools(response, messages)
        response = tools_response if tools_response else response
        message = [{"role": "assistant", "content": response}]
        self.memory.add_messages_to_conversation(message, user_id, self.name, conversation_id)
        return response

    def generate_response_stream(self, prompt: str, user_id: str, conversation_id: str = None) -> Generator[str]:
        messages = self._compose_messages_list(prompt, user_id, conversation_id)
        stream = self.completions.generate_response(messages, model=self.model, stream=True)
        response = ""
        for chunk in stream:
            response += chunk
            if not response.startswith("{"):
                yield chunk

        # TODO: handle logic with functions and stream
        message = [{"role": "assistant", "content": response}]
        self.memory.add_messages_to_conversation(message, user_id, self.name, conversation_id)
        return response


class BaseAsyncAgent(AsyncAIAgentInterface):
    name = "base"
    model_provider = os.getenv("DEFAULT_MODEL_PROVIDER", "openai")
    memory_provider = os.getenv("DEFAULT_MEMORY_PROVIDER", "aioredis")
    tools = None
    system_prompt = (
        "You are an AI assistant. The assistant is helpful, creative,"
        "clever, and very friendly. You help users with his tasks and answers his questions."
        "The assistant is very good at understanding context and subtext. The assistant is "
        "very good at understanding natural language."
    )

    async def _compose_messages_list(
        self, prompt: str, user_id: Union[str, int], conversation_id: Union[str, int]
    ) -> list[dict]:
        instruction = self.system_prompt
        if self.tools_registry:
            instruction += f"\n{prompts.FUNCTION_INSTRUCTION}"
            schemes = [tool.llm_schema for tool in self.tools_registry.values()]
            instruction += f"\n{json.dumps(schemes)}"
        system_messages = [{"role": "system", "content": instruction}]
        conversation_history = await self.async_get_conversation(user_id, conversation_id)
        user_message = [{"role": "user", "content": prompt}]
        await self.memory.async_add_messages_to_conversation(user_message, user_id, self.name, conversation_id)
        return system_messages + conversation_history + user_message

    async def _check_tools(self, response: str, conversation_list: list) -> dict:
        response = invoker.parse_llm_response(response)
        message = []
        while response["type"] == "function":
            # TODO: possible infinite loop. To handle (bot created 10 records)
            result = invoker.trigger_function(response, self.tools_registry)
            fname = response["name"]
            try:
                if inspect.iscoroutine(result):
                    result = await result
                message += [
                    {
                        "role": "developer",
                        "content": f"You successfully triggered a function {fname} and it returned: {result}",
                    }
                ]
            except Exception as e:
                message += [
                    {
                        "role": "developer",
                        "content": f"You tried to trigger function {fname} but excepthion was rised: {e}",
                    }
                ]
            response = await self.completions.async_generate_response(conversation_list + message, model=self.model)
            response = invoker.parse_llm_response(response)
        return response["content"]

    def register_tool(self, tool):
        if not hasattr(tool, "llm_schema"):
            raise TypeError(f"Cant register tool {tool.__name__}: no scheme")
        self.tools_registry[tool.__name__] = tool

    def init_agent(self, *args, **kwargs) -> dict:
        self.memory = AsyncMemoryProviderBuilder.build(self.memory_provider)
        self.completions = AsyncCompletionsClientBuilder.build(kwargs.get("provider") or self.model_provider)
        self.system_prompt = kwargs.get("system_prompt") or self.system_prompt
        self.model = kwargs.get("model")
        self.tools_registry = {}
        for tool in kwargs.get("tools") or self.tools or []:
            self.register_tool(tool)

    async def async_get_conversation(self, user_id: str, conversation_id: str = None) -> list[dict]:
        conversation = await self.memory.async_get_conversation(user_id, self.name, conversation_id)
        return conversation or []

    async def async_clear_conversation(self, user_id: str, conversation_id: str = None) -> bool:
        return await self.memory.async_delete_conversation(user_id, self.name, conversation_id)

    async def async_generate_response(self, prompt: str, user_id: str, conversation_id: str = None) -> str:
        messages = await self._compose_messages_list(prompt, user_id, conversation_id)
        response = await self.completions.async_generate_response(messages, model=self.model)
        response = await self._check_tools(response, messages)
        message = [{"role": "assistant", "content": response}]
        await self.memory.async_add_messages_to_conversation(message, user_id, self.name, conversation_id)
        return response

    async def async_generate_response_stream(
        self, prompt: str, user_id: str, conversation_id: str = None
    ) -> AsyncGenerator[str]:
        messages = self._compose_messages_list(prompt, user_id, conversation_id)
        stream = await self.completions.async_generate_response(messages, model=self.model, stream=True)
        response = ""
        async for chunk in stream:
            response += chunk
            if not response.startswith("{"):
                yield chunk

        # TODO: handle logic with functions and stream
        message = [{"role": "assistant", "content": response}]
        await self.memory.async_add_messages_to_conversation(message, user_id, self.name, conversation_id)
        yield response

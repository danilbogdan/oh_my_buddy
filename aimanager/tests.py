import unittest
from unittest.mock import Mock, patch
from aimanager.memory.builder import MemoryProviderBuilder
from aimanager.completions.builder import CompletionsClientBuilder
from aimanager.agent.builder import LLMAgentBuilder
from aimanager.completions.openai import OpenAIProvider
from aimanager.completions.lmstudio import LMStudioProvider
from aimanager.completions.openrouter import OpenRouterProvider
from aimanager.agent._base import BaseAgent


class TestMemoryProviderBuilder(unittest.TestCase):
    def test_build_mem0_provider(self):
        provider = MemoryProviderBuilder.build("mem0")
        self.assertIsNotNone(provider)

    def test_build_redis_provider(self):
        provider = MemoryProviderBuilder.build("redis")
        self.assertIsNotNone(provider)

    def test_invalid_provider(self):
        with self.assertRaises(NotImplementedError):
            MemoryProviderBuilder.build("invalid")


class TestCompletionsClientBuilder(unittest.TestCase):
    def test_build_openai_provider(self):
        provider = CompletionsClientBuilder.build("openai")
        self.assertIsInstance(provider, OpenAIProvider)

    def test_build_lmstudio_provider(self):
        provider = CompletionsClientBuilder.build("lmstudio")
        self.assertIsInstance(provider, LMStudioProvider)

    def test_build_openrouter_provider(self):
        provider = CompletionsClientBuilder.build("openrouter")
        self.assertIsInstance(provider, OpenRouterProvider)

    def test_invalid_provider(self):
        with self.assertRaises(ValueError):
            CompletionsClientBuilder.build("invalid")


class TestOpenAIProvider(unittest.TestCase):
    @patch("openai.OpenAI")
    def test_generate_response(self, mock_openai):
        mock_completion = Mock()
        mock_completion.choices[0].message.content = "Test response"
        mock_openai.return_value.chat.completions.create.return_value = mock_completion

        provider = OpenAIProvider()
        response = provider.generate_response(messages=[{"role": "user", "content": "test"}])
        self.assertEqual(response, "Test response")


class TestBaseAgent(unittest.TestCase):
    def setUp(self):
        self.agent = BaseAgent()

    def test_init_agent(self):
        self.assertIsNotNone(self.agent.memory)
        self.assertIsNotNone(self.agent.completions)

    @patch("aimanager.agent._base.CompletionsClientBuilder")
    @patch("aimanager.agent._base.MemoryProviderBuilder")
    def test_generate_response(self, mock_memory_builder, mock_completions_builder):
        mock_memory = Mock()
        mock_memory.get_conversation.return_value = []
        mock_memory_builder.build.return_value = mock_memory

        mock_completions = Mock()
        mock_completions.generate_response.return_value = "Test response"
        mock_completions_builder.build.return_value = mock_completions

        agent = BaseAgent()
        response = agent.generate_response("test prompt", "user123")
        self.assertEqual(response, "Test response")

    def test_clear_conversation(self):
        with patch.object(self.agent.memory, "delete_conversation", return_value=True):
            result = self.agent.clear_conversation("user123")
            self.assertTrue(result)


class TestLLMAgentBuilder(unittest.TestCase):
    def test_build_base_agent(self):
        agent = LLMAgentBuilder.build("base")
        self.assertIsInstance(agent, BaseAgent)

    def test_build_with_missing_params(self):
        with self.assertRaises(ValueError):
            LLMAgentBuilder.build(None)


if __name__ == "__main__":
    unittest.main()

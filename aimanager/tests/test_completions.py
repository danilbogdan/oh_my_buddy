import unittest
from unittest.mock import Mock, patch
from aimanager.completions.builder import CompletionsClientBuilder
from aimanager.completions.openai import OpenAIProvider
from aimanager.completions.lmstudio import LMStudioProvider
from aimanager.completions.openrouter import OpenRouterProvider


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
    def test_generate_response(self):
        provider = OpenAIProvider()
        provider.client = Mock()
        mock_completion = Mock()
        mock_choice = Mock()
        mock_choice.message.content = "Test response"
        mock_completion.choices = [mock_choice]
        provider.client.chat.completions.create.return_value = mock_completion
        for response in provider.generate_response(messages=[{"role": "user", "content": "test"}]):
            self.assertEqual(response, "Test response")


if __name__ == "__main__":
    unittest.main() 
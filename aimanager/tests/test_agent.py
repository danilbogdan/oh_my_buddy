import unittest
from unittest.mock import Mock, patch

from aimanager.agent._base import BaseAgent
from aimanager.agent.builder import LLMAgentBuilder


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
        agent = LLMAgentBuilder.build(None)
        self.assertIsInstance(agent, BaseAgent)


if __name__ == "__main__":
    unittest.main() 
from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Conversation
from ..repositories.conversation import ConversationRepository
from ..repositories.provider_config import ProviderConfigRepository


class ConversationRepositoryTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.repo = ConversationRepository()
        self.metadata = {"model": "gpt-4", "provider": "openai"}

    def test_create_conversation(self):
        conv = self.repo.create(self.user, metadata=self.metadata)
        self.assertIsInstance(conv, Conversation)
        self.assertEqual(conv.user, self.user)
        self.assertEqual(conv.metadata, self.metadata)

    def test_get_conversation(self):
        created_conv = self.repo.create(self.user, title="Test", metadata=self.metadata)
        retrieved_conv = self.repo.get(created_conv.id)
        self.assertEqual(retrieved_conv.id, created_conv.id)
        self.assertEqual(retrieved_conv.title, "Test")

    def test_list_user_conversations(self):
        self.repo.create(self.user, title="Chat 1", metadata=self.metadata)
        self.repo.create(self.user, title="Chat 2", metadata=self.metadata)

        conversations = self.repo.list(self.user)
        self.assertEqual(len(conversations), 2)

    def test_update_conversation(self):
        conv = self.repo.create(self.user, title="Original", metadata=self.metadata)
        updated_conv = self.repo.update(conv.id, title="Updated")
        self.assertEqual(updated_conv.title, "Updated")

    def test_delete_conversation(self):
        conv = self.repo.create(self.user, metadata=self.metadata)
        self.assertTrue(self.repo.delete(conv.id))
        self.assertIsNone(self.repo.get(conv.id))


class ProviderConfigRepositoryTest(TestCase):
    def setUp(self):
        self.repo = ProviderConfigRepository()

    def test_get_default_config(self):
        config = self.repo.get_config()
        self.assertEqual(config.model, "gpt-4o-mini")
        self.assertEqual(config.provider, "openai")
        self.assertEqual(config.agent, "base")

    def test_update_config(self):
        updated_config = self.repo.update_config(model="gpt-4", provider="openrouter", agent="custom")
        self.assertEqual(updated_config.model, "gpt-4")
        self.assertEqual(updated_config.provider, "openrouter")
        self.assertEqual(updated_config.agent, "custom")

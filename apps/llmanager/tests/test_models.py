from django.test import TestCase
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from ..models import Conversation, DefaultConfig


class ConversationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.metadata = {"model": "gpt-4", "provider": "openai"}

    def test_create_conversation(self):
        conversation = Conversation.objects.create(user=self.user, title="Test Chat", metadata=self.metadata)
        self.assertEqual(conversation.title, "Test Chat")
        self.assertEqual(conversation.user, self.user)
        self.assertEqual(conversation.metadata, self.metadata)

    def test_conversation_str(self):
        conversation = Conversation.objects.create(user=self.user, title="Test Chat", metadata=self.metadata)
        self.assertEqual(str(conversation), "Test Chat")

    def test_conversation_requires_user(self):
        with self.assertRaises(IntegrityError):
            Conversation.objects.create(title="Test Chat", metadata=self.metadata)


class DefaultConfigModelTest(TestCase):
    def test_create_default_config(self):
        config = DefaultConfig.objects.create()
        self.assertEqual(config.model, "gpt-4o-mini")
        self.assertEqual(config.provider, "openai")
        self.assertEqual(config.agent, "base")

    def test_singleton_behavior(self):
        DefaultConfig.objects.create()
        DefaultConfig.objects.create()

        # Should only have one instance
        self.assertEqual(DefaultConfig.objects.count(), 1)

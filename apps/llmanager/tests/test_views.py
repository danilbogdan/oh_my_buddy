from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Conversation


class ConversationViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.client.force_authenticate(user=self.user)
        self.metadata = {"model": "gpt-4", "provider": "openai"}

    def test_create_conversation(self):
        response = self.client.post(reverse("conversation-list"), data={"metadata": self.metadata}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertIn("title", response.data)

    def test_list_conversations(self):
        # Create some test conversations
        Conversation.objects.create(user=self.user, title="Chat 1", metadata=self.metadata)
        Conversation.objects.create(user=self.user, title="Chat 2", metadata=self.metadata)

        response = self.client.get(reverse("conversation-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_conversation(self):
        conv = Conversation.objects.create(user=self.user, title="Test Chat", metadata=self.metadata)
        response = self.client.get(reverse("conversation-detail", kwargs={"pk": conv.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Chat")

    def test_update_conversation(self):
        conv = Conversation.objects.create(user=self.user, title="Original", metadata=self.metadata)
        response = self.client.patch(
            reverse("conversation-detail", kwargs={"pk": conv.id}), {"title": "Updated"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated")

    def test_delete_conversation(self):
        conv = Conversation.objects.create(user=self.user, title="Test", metadata=self.metadata)
        response = self.client.delete(reverse("conversation-detail", kwargs={"pk": conv.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Conversation.objects.filter(id=conv.id).exists())

    def test_unauthorized_access(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse("conversation-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

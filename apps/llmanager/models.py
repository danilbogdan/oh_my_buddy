from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth import get_user_model
from solo.models import SingletonModel


User = get_user_model()


class DefaultConfig(SingletonModel):
    model = models.CharField(max_length=255, default="gpt-4o-mini")
    provider = models.CharField(max_length=255, default="openai")
    agent = models.CharField(max_length=255, default="base")


class Agent(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    instructions = models.TextField()
    model = models.CharField(max_length=255, default="gpt-4-mini")
    provider = models.CharField(max_length=255, default="openai")
    metadata = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Agent")
        verbose_name_plural = _("Agents")

    def __str__(self):
        return self.name


class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = _("Conversation")
        verbose_name_plural = _("Conversations")

    def __str__(self):
        return f"Conversation {self.id} for User {self.user.username}"



# class LLModel(models.Model):
#     name = models.CharField(max_length=255)
#     description = models.TextField()

#     class Meta:
#         verbose_name = _("LLModel")
#         verbose_name_plural = _("LLModels")

#     def __str__(self):
#         return self.name


# class Assistant(models.Model):
#     instructions = models.TextField()
#     name = models.CharField(max_length=255)
#     tools = models.JSONField()
#     model = models.ForeignKey(LLModel, on_delete=models.CASCADE)

#     class Meta:
#         verbose_name = _("Assistant")
#         verbose_name_plural = _("Assistants")

#     def __str__(self):
#         return self.name

# class Message(models.Model):
#     thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
#     role = models.CharField(max_length=50)
#     content = models.TextField()
#     metadata = models.JSONField()

#     class Meta:
#         verbose_name = _("Message")
#         verbose_name_plural = _("Messages")

#     def __str__(self):
#         return f"Message {self.id} in Thread {self.thread.id}"

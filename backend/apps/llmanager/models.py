from django.db import models
from solo.models import SingletonModel


# Create your models here.
class LLMProviderConfig(SingletonModel):
    system_instruction = models.TextField(
        "System Instruction",
        help_text="This is the instruction that the AI will use to generate responses.",
        default="You are a helpful personal assistant.",
    )
    provider = models.CharField(
        "Provider",
        max_length=255,
        help_text="The provider that the AI will use to generate responses.",
        default="openai",
    )
    model = models.CharField(
        "Model",
        max_length=255,
        help_text="The model that the AI will use to generate responses.",
        default="gpt-4o",
    )

    def __str__(self):
        return "Site Configuration"

    class Meta:
        verbose_name = "LLM Provider Configuration"

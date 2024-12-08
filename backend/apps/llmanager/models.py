from django.utils.translation import gettext_lazy as _
from django.db import models
from solo.models import SingletonModel


# Create your models here.
class LLMProviderConfig(SingletonModel):
    system_instruction = models.TextField(
        "System Instruction",
        help_text="This is the instruction that the AI will use to generate responses.",
        default="You are a helpful personal assistant.",
    )
    provider = models.ForeignKey(
        "llmanager.LLMProvider",
        on_delete=models.CASCADE,
        help_text="The provider that the AI will use to generate responses.",
        null=True,
    )
    model = models.ForeignKey(
        "llmanager.LLModel",
        on_delete=models.CASCADE,
        help_text="The model that the AI will use to generate responses.",
        null=True,
    )

    def __str__(self):
        return "Site Configuration"

    class Meta:
        verbose_name = "LLM Provider Configuration"


class LLModel(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        verbose_name = _("LLModel")
        verbose_name_plural = _("LLModels")

    def __str__(self):
        return self.name


class LLMProvider(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    model = models.ForeignKey(LLModel, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("LLMProvider")
        verbose_name_plural = _("LLMProviders")

    def __str__(self):
        return self.name
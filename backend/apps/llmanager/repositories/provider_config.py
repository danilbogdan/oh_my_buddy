from apps.llmanager.models import LLMProviderConfig


class ProviderConfigRepository:

    @classmethod
    def get_model(cls):
        return LLMProviderConfig.get_solo().model.name

    @classmethod
    def get_system_instruction(cls):
        return LLMProviderConfig.get_solo().system_instruction

    @classmethod
    def get_provider(cls):
        return LLMProviderConfig.get_solo().provider.name

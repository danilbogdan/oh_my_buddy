from apps.llmanager.models import DefaultConfig


class ConfigRepository:

    @classmethod
    def get_default(cls):
        return DefaultConfig.get_solo()

    @classmethod
    def get_agent(cls):
        return DefaultConfig.get_solo().agent

    @classmethod
    def get_provider(cls):
        return DefaultConfig.get_solo().provider

    @classmethod
    def get_model(cls):
        return DefaultConfig.get_solo().model

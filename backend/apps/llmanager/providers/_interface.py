from abc import ABC, abstractmethod


class LLMProviderInterface(ABC):

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass

from abc import ABC, abstractmethod


class AIAgentInterface(ABC):

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.init_agent(*args, **kwargs)

    @abstractmethod
    def init_agent(self, instructions: str, name: str, tools: list, model: str) -> dict:
        pass

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass

    @abstractmethod
    def generate_response_stream(self, prompt: str) -> str:
        pass

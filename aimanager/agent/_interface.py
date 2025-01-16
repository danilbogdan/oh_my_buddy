from abc import ABC, abstractmethod
from typing import Generator


class AIAgentInterface(ABC):

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.init_agent(*args, **kwargs)

    @abstractmethod
    def init_agent(self, instructions: str, name: str, tools: list, model: str) -> dict:
        pass

    @abstractmethod
    def get_conversation(self, user_id: str, conversation_id: str = None) -> list[dict]:
        pass

    @abstractmethod
    def clear_conversation(self, user_id: str, conversation_id: str = None) -> bool:
        pass

    @abstractmethod
    def generate_response(self, prompt: str, user_id: str, conversation_id: str = None) -> str:
        pass

    @abstractmethod
    def generate_response_stream(self, prompt: str, user_id: str, conversation_id: str = None) -> Generator[str]:
        pass

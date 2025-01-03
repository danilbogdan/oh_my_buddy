from abc import ABC, abstractmethod


class MemoryProviderInterface(ABC):

    @abstractmethod
    def init_memory(self, *args, **kwargs) -> dict:
        pass

    @abstractmethod
    def save_conversation_to_memory(self, data: list[dict]) -> dict:
        pass

    @abstractmethod
    def get_from_memory(self, query: str) -> dict:
        pass

    @abstractmethod
    def clear_memory(self) -> dict:
        pass
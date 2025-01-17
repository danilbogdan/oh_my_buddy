from abc import ABC, abstractmethod


class MemoryProviderInterface(ABC):

    @abstractmethod
    def init_memory(self, *args, **kwargs) -> dict:
        pass

    @abstractmethod
    def add_messages_to_conversation(self, message: list[dict], user_id: str, agent_id: str, conversation_id: str) -> None:
        pass

    @abstractmethod
    def get_conversation(self, user_id: str, agent_id: str, conversation_id: str) -> list[dict]:
        pass

    @abstractmethod
    def delete_conversation(self, user_id: str, agent_id: str, conversation_id: str) -> dict:
        pass

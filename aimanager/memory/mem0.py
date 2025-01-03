import os

from mem0 import MemoryClient

from .interface import MemoryProviderInterface


class Mem0MemoryProvider(MemoryProviderInterface):

    def __init__(self, *args, **kwargs):
        self.client = None
        self.init_memory(*args, **kwargs)

    def init_memory(self, *args, **kwargs) -> dict:
        api_key = kwargs.get("api_key") or os.getenv("MEM0_API_KEY")
        self.client = MemoryClient(api_key=api_key)

    def save_conversation_to_memory(self, data: list[dict], user_id: str, agent_id: str) -> dict:
        self.client.add(data, user_id=user_id, agent_id=agent_id)

    def get_from_memory(self, query: str, user_id: str, agent_id: str) -> dict:
        return self.client.search(query, user_id=user_id, agent_id=agent_id)

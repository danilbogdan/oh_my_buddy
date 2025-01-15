import os
import redis
import json

from .interface import MemoryProviderInterface


class RedisMemoryProvider(MemoryProviderInterface):

    def __init__(self, *args, **kwargs):
        self.client = None
        self.init_memory(*args, **kwargs)

    def init_memory(self, *args, **kwargs) -> dict:
        redis_url = kwargs.get("redis_url") or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.client = redis.StrictRedis.from_url(redis_url)

    def save_conversation(self, data: list[dict], user_id: str, agent_id: str, conversation_id: str) -> None:
        key = f"{conversation_id}:{user_id}:{agent_id}:conversation"
        json_data = [json.dumps(item) for item in data]
        self.client.rpush(key, *json_data)

    def get_conversation(self, user_id: str, agent_id: str, conversation_id: str) -> list[dict]:
        key = f"{conversation_id}:{user_id}:{agent_id}:conversation"
        data = self.client.lrange(key, 0, -1)
        return [json.loads(item) for item in data]
    
    def delete_conversation(self, user_id: str, agent_id: str, conversation_id: str) -> dict:
        key = f"{conversation_id}:{user_id}:{agent_id}:conversation"
        self.client.delete(key)

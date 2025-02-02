import json
import logging
import os

import redis
import redis.asyncio as aredis

from .interface import AsyncMemoryProviderInterface, MemoryProviderInterface

logger = logging.getLogger("django")


class RedisMemoryProvider(MemoryProviderInterface):
    def __init__(self, *args, **kwargs):
        self.client = None
        self.init_memory(*args, **kwargs)

    def init_memory(self, *args, **kwargs) -> dict:
        redis_url = kwargs.get("redis_url") or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.client = redis.StrictRedis.from_url(redis_url)

    def add_messages_to_conversation(self, data: list[dict], user_id: str, agent_id: str, conversation_id: str) -> None:
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


class AIORedisMemoryProvider(AsyncMemoryProviderInterface):
    def __init__(self, *args, **kwargs):
        self.client = None
        self.init_memory(*args, **kwargs)

    def init_memory(self, *args, **kwargs) -> dict:
        redis_url = kwargs.get("redis_url") or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        pool = aredis.ConnectionPool.from_url(redis_url)
        self.client = aredis.Redis.from_pool(pool)

    async def async_add_messages_to_conversation(
        self, data: list[dict], user_id: str, agent_id: str, conversation_id: str
    ) -> None:
        key = f"{conversation_id}:{user_id}:{agent_id}:conversation"
        logger.info(key, data)
        json_data = [json.dumps(item) for item in data]
        await self.client.rpush(key, *json_data)

    async def async_get_conversation(self, user_id: str, agent_id: str, conversation_id: str) -> list[dict]:
        key = f"{conversation_id}:{user_id}:{agent_id}:conversation"
        data = await self.client.lrange(key, 0, -1)
        return [json.loads(item) for item in data]

    async def async_delete_conversation(self, user_id: str, agent_id: str, conversation_id: str) -> dict:
        key = f"{conversation_id}:{user_id}:{agent_id}:conversation"
        await self.client.delete(key)

    async def async_close(self):
        self.client.close()
        await self.client.wait_closed()

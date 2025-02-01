from .mem0 import Mem0MemoryProvider
from .redis import AIORedisMemoryProvider, RedisMemoryProvider
from .interface import MemoryProviderInterface, AsyncMemoryProviderInterface


class MemoryProviderBuilder:

    @staticmethod
    def build(provider_name: str, *args, **kwargs) -> MemoryProviderInterface: 
        if provider_name == "mem0":
            return Mem0MemoryProvider(*args, **kwargs)
        if provider_name == "redis":
            return RedisMemoryProvider(*args, **kwargs)
        else:
            raise NotImplementedError(f"Memory provider {provider_name} is not implemented")


class AsyncMemoryProviderBuilder:

    @staticmethod
    def build(provider_name: str, *args, **kwargs) -> AsyncMemoryProviderInterface:
        return AIORedisMemoryProvider(*args, **kwargs)

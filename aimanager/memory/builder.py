from .mem0 import Mem0MemoryProvider
from .redis import RedisMemoryProvider


class MemoryProviderBuilder:

    @staticmethod
    def build(provider_name: str, *args, **kwargs):
        if provider_name == "mem0":
            return Mem0MemoryProvider(*args, **kwargs)
        if provider_name == "redis":
            return RedisMemoryProvider(*args, **kwargs)
        else:
            raise NotImplementedError(f"Memory provider {provider_name} is not implemented")

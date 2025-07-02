import unittest
from aimanager.memory.builder import MemoryProviderBuilder


class TestMemoryProviderBuilder(unittest.TestCase):
    def test_build_mem0_provider(self):
        provider = MemoryProviderBuilder.build("mem0")
        self.assertIsNotNone(provider)

    def test_build_redis_provider(self):
        provider = MemoryProviderBuilder.build("redis")
        self.assertIsNotNone(provider)

    def test_invalid_provider(self):
        with self.assertRaises(NotImplementedError):
            MemoryProviderBuilder.build("invalid")


if __name__ == "__main__":
    unittest.main() 
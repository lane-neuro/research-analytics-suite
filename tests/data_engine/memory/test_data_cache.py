import pytest

from research_analytics_suite.data_engine.memory.DataCache import DataCache


@pytest.fixture(scope='class')
async def data_cache():
    cache = DataCache()
    await cache.initialize()
    return cache


class TestDataCache:

    @pytest.fixture(autouse=True)
    async def setup_class(self, data_cache):
        self.cache = data_cache

    @pytest.mark.asyncio
    async def test_data_cache_initialization(self):
        assert self.cache._initialized

    def test_data_cache_set_get(self):
        self.cache.set("key", "value")
        assert self.cache.get("key") == "value"

    def test_data_cache_clear(self):
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.clear()
        assert self.cache.get("key1") is None
        assert self.cache.get("key2") is None

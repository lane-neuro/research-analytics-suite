import pytest
import asyncio
from unittest import mock

import pytest_asyncio

from research_analytics_suite.data_engine import DataCache


@pytest.fixture
def mock_custom_logger():
    with mock.patch('research_analytics_suite.utils.CustomLogger') as mock_logger:
        yield mock_logger


@pytest.fixture
def mock_workspace():
    with mock.patch('research_analytics_suite.data_engine.Workspace') as mock_workspace:
        yield mock_workspace


@pytest_asyncio.fixture
async def data_cache(mock_custom_logger, mock_workspace):
    cache = DataCache()
    await cache.initialize()
    return cache


class TestDataCache:
    def test_singleton(self, data_cache):
        another_cache_instance = DataCache()
        assert data_cache is another_cache_instance

    def test_initialize(self, data_cache):
        assert data_cache._initialized is True
        assert data_cache._cache is not None

    def test_get_set(self, data_cache):
        data_cache.set('test_key', 'test_value')
        assert data_cache.get('test_key') == 'test_value'

    def test_clear(self, data_cache):
        data_cache.set('test_key', 'test_value')
        data_cache.clear()
        assert data_cache.get('test_key') is None

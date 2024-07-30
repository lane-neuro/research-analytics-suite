import asyncio
import json
import os
from unittest.mock import MagicMock, patch

import aiofiles
import psutil
import pytest
import pytest_asyncio

from research_analytics_suite.utils import Config


@pytest_asyncio.fixture
async def config():
    config_instance = Config()
    await config_instance.initialize()
    return config_instance


class TestConfig:

    @pytest.mark.asyncio
    async def test_singleton(self):
        config1 = await Config().initialize()
        config2 = await Config().initialize()
        assert config1 is config2

    def test_default_values(self, config):
        config_instance = config
        assert config_instance.WORKSPACE_NAME == 'default_workspace'
        assert config_instance.MEMORY_LIMIT == psutil.virtual_memory().total * 0.5
        assert config_instance.DEBUG_CONSOLE is False
        assert config_instance.DB_HOST == 'localhost'

    @pytest.mark.asyncio
    async def test_update_setting(self, config):
        config_instance = config
        await config_instance.update_setting('DEBUG_CONSOLE', 'DEBUG')
        assert config_instance.DEBUG_CONSOLE == 'DEBUG'

        with pytest.raises(AttributeError):
            await config_instance.update_setting('NON_EXISTENT_SETTING', 'value')

    @pytest.mark.asyncio
    async def test_reload(self, config):
        with patch('research_analytics_suite.utils.CustomLogger', MagicMock()) as mock_logger:
            config_instance = config
            new_config = {
                'DEBUG_CONSOLE': 'DEBUG',
                'DB_HOST': '127.0.0.1',
            }

            await config_instance.reload(new_config)
            assert config_instance.DEBUG_CONSOLE == 'DEBUG'
            assert config_instance.DB_HOST == '127.0.0.1'

    @pytest.mark.asyncio
    async def test_reload_from_file(self, config, tmp_path):
        config_instance = config
        file_path = tmp_path / "config.json"
        new_config = {
            'DEBUG_CONSOLE': 'DEBUG',
            'DB_HOST': '127.0.0.1',
        }
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(json.dumps(new_config))

        with patch('research_analytics_suite.utils.CustomLogger', MagicMock()) as mock_logger:
            mock_logger.add_file_handlers = MagicMock()
            await config_instance.reload_from_file(str(file_path))
            assert config_instance.DEBUG_CONSOLE == 'DEBUG'
            assert config_instance.DB_HOST == '127.0.0.1'

    @pytest.mark.asyncio
    async def test_save_to_file(self, config, tmp_path):
        config_instance = config
        # Reset configuration to default values before saving
        config_instance.reset_to_defaults()

        file_path = tmp_path / "config_saved.json"
        await config_instance.save_to_file(str(file_path))

        async with aiofiles.open(file_path, 'r') as f:
            saved_config = json.loads(await f.read())

        assert saved_config['WORKSPACE_NAME'] == 'default_workspace'
        assert saved_config['DEBUG_CONSOLE'] is False

    @pytest.mark.asyncio
    async def test_reload_non_existent_setting(self, config):
        config_instance = config
        new_config = {
            'NON_EXISTENT_SETTING': 'value',
        }
        with pytest.raises(AttributeError):
            await config_instance.reload(new_config)

    @pytest.mark.asyncio
    async def test_reload_file_path_no_json_extension(self, config, tmp_path):
        with patch('research_analytics_suite.utils.CustomLogger', MagicMock()) as mock_logger:
            mock_logger.add_file_handlers = MagicMock()

            config_instance = config
            dir_path = tmp_path / "config_dir"
            os.makedirs(dir_path)

            file_path = dir_path / "config.json"
            new_config = {
                'DEBUG_CONSOLE': 'DEBUG',
                'DB_HOST': '127.0.0.1',
            }
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(json.dumps(new_config))

            await config_instance.reload_from_file(str(dir_path))
            assert config_instance.DEBUG_CONSOLE == 'DEBUG'
            assert config_instance.DB_HOST == '127.0.0.1'

    @pytest.mark.asyncio
    async def test_reload_file_not_exists(self, config):
        config_instance = config
        non_existent_file_path = "/non/existent/path/config.json"
        with pytest.raises(FileNotFoundError):
            await config_instance.reload_from_file(non_existent_file_path)

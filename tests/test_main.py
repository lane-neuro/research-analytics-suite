# test_main.py

import pytest
import asyncio
from unittest import mock
import sys

# Import the main function from the script
from research_analytics_suite import __main__ as main


@pytest.fixture
def mock_apply():
    with mock.patch('nest_asyncio.apply') as mock_apply:
        yield mock_apply


@pytest.fixture
def mock_run():
    with mock.patch('asyncio.run') as mock_run:
        yield mock_run


@pytest.fixture
def mock_sys_exit():
    with mock.patch('sys.exit') as mock_sys_exit:
        yield mock_sys_exit


@pytest.fixture
def mock_get_event_loop():
    with mock.patch('asyncio.get_event_loop') as mock_get_event_loop:
        yield mock_get_event_loop


@pytest.mark.asyncio
async def test_main(mock_apply, mock_run, mock_sys_exit, mock_get_event_loop):
    mock_event_loop = mock.Mock()
    mock_get_event_loop.return_value = mock_event_loop

    with mock.patch.object(sys, 'argv', ['__main__.py', '-o', 'default_workspace']):
        main()

    mock_apply.assert_called_once()
    mock_run.assert_called_once()
    mock_get_event_loop.assert_called_once()
    mock_event_loop.close.assert_called_once()
    mock_sys_exit.assert_called_once_with(0)


@pytest.mark.asyncio
async def test_main_keyboard_interrupt(mock_apply, mock_run, mock_sys_exit, mock_get_event_loop):
    mock_run.side_effect = KeyboardInterrupt
    mock_event_loop = mock.Mock()
    mock_get_event_loop.return_value = mock_event_loop

    with mock.patch.object(sys, 'argv', ['__main__.py', '-o', 'default_workspace']):
        main()

    mock_apply.assert_called_once()
    mock_run.assert_called_once()
    mock_get_event_loop.assert_called_once()
    mock_event_loop.close.assert_called_once()
    mock_sys_exit.assert_called_once_with(0)


@pytest.mark.asyncio
async def test_main_exception(mock_apply, mock_run, mock_sys_exit, mock_get_event_loop):
    mock_run.side_effect = Exception('Test Exception')
    mock_event_loop = mock.Mock()
    mock_get_event_loop.return_value = mock_event_loop

    with mock.patch.object(sys, 'argv', ['__main__.py', '-o', 'default_workspace']):
        main()

    mock_apply.assert_called_once()
    mock_run.assert_called_once()
    mock_get_event_loop.assert_called_once()
    mock_event_loop.close.assert_called_once()
    mock_sys_exit.assert_called_once_with(0)

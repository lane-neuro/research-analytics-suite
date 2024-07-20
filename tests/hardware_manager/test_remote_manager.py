import pytest
from unittest import mock
import paramiko

from research_analytics_suite.hardware_manager.RemoteManager import RemoteManager


class TestRemoteManager:
    @pytest.fixture
    def logger(self):
        with mock.patch('research_analytics_suite.utils.CustomLogger') as logger:
            yield logger

    @pytest.fixture
    def remote_manager(self, logger):
        return RemoteManager(logger, 'path/to/known_hosts')

    def test_initialization(self, remote_manager, logger):
        assert remote_manager.logger == logger
        assert remote_manager.remote_servers == []

    def test_initialization_with_remote_servers(self, logger):
        remote_servers = [{'hostname': 'server1', 'username': 'user1', 'password': 'pass1'}]
        remote_manager = RemoteManager(logger, 'path/to/known_hosts', remote_servers)
        assert remote_manager.logger == logger
        assert remote_manager.remote_servers == remote_servers

    def test_connect_to_remote_server_success(self, remote_manager, logger):
        with mock.patch('paramiko.SSHClient') as MockSSHClient, \
             mock.patch('paramiko.RejectPolicy') as MockRejectPolicy:
            mock_ssh = MockSSHClient.return_value
            mock_ssh.connect.return_value = None

            ssh = remote_manager.connect_to_remote_server('hostname', 'username', 'password')
            assert ssh == mock_ssh
            mock_ssh.load_system_host_keys.assert_called_once()
            mock_ssh.load_host_keys.assert_called_once_with('path/to/known_hosts')
            mock_ssh.set_missing_host_key_policy.assert_called_once_with(MockRejectPolicy.return_value)
            mock_ssh.connect.assert_called_once_with('hostname', username='username', password='password')
            logger.info.assert_any_call("Connecting to remote server hostname...")
            logger.info.assert_any_call("Connected to hostname")

    def test_connect_to_remote_server_failure(self, remote_manager, logger):
        with mock.patch('paramiko.SSHClient') as MockSSHClient, \
             mock.patch('paramiko.RejectPolicy') as MockRejectPolicy:
            mock_ssh = MockSSHClient.return_value
            mock_ssh.connect.side_effect = paramiko.ssh_exception.SSHException("Connection error")

            ssh = remote_manager.connect_to_remote_server('hostname', 'username', 'password')
            assert ssh is None
            mock_ssh.load_system_host_keys.assert_called_once()
            mock_ssh.load_host_keys.assert_called_once_with('path/to/known_hosts')
            mock_ssh.set_missing_host_key_policy.assert_called_once_with(MockRejectPolicy.return_value)
            logger.info.assert_any_call("Connecting to remote server hostname...")
            logger.error.assert_any_call("Failed to connect to hostname: Connection error")

    def test_manage_remote_server_success(self, remote_manager, logger):
        server_info = {'hostname': 'server1', 'username': 'user1', 'password': 'pass1'}
        command = "python -c 'print(sum(i*i for i in range(1000000)))'"

        with mock.patch.object(remote_manager, 'connect_to_remote_server', return_value=mock.Mock()) as mock_connect:
            mock_ssh = mock_connect.return_value
            mock_ssh.exec_command.return_value = (None, mock.Mock(), None)
            mock_ssh.exec_command.return_value[1].read.return_value = b"499999500000"

            remote_manager.manage_remote_server(server_info, command)
            mock_connect.assert_called_once_with('server1', 'user1', 'pass1')
            logger.info.assert_any_call("Managing tasks on remote server server1...")
            logger.info.assert_any_call("Output from remote server server1: 499999500000")

    def test_manage_remote_server_connection_failure(self, remote_manager, logger):
        server_info = {'hostname': 'server1', 'username': 'user1', 'password': 'pass1'}
        command = "python -c 'print(sum(i*i for i in range(1000000)))'"

        with mock.patch.object(remote_manager, 'connect_to_remote_server', return_value=None):
            remote_manager.manage_remote_server(server_info, command)
            logger.error.assert_any_call("Failed to connect to server1: Connection error")

    def test_manage_remote_server_task_failure(self, remote_manager, logger):
        server_info = {'hostname': 'server1', 'username': 'user1', 'password': 'pass1'}
        command = "python -c 'print(sum(i*i for i in range(1000000)))'"

        with mock.patch.object(remote_manager, 'connect_to_remote_server', return_value=mock.Mock()) as mock_connect:
            mock_ssh = mock_connect.return_value
            mock_ssh.exec_command.side_effect = Exception("Execution error")

            remote_manager.manage_remote_server(server_info, command)
            logger.info.assert_any_call("Managing tasks on remote server server1...")
            logger.error.assert_any_call("Error managing tasks on remote server server1: Execution error")

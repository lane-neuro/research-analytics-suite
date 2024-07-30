import subprocess

import pytest
from unittest.mock import patch, MagicMock
import socket
from typing import List, Dict, Any

from research_analytics_suite.hardware_manager.interface.network.Ethernet import Ethernet


@pytest.fixture
def logger():
    return MagicMock()


@pytest.fixture
@patch('platform.system', return_value='Linux')
def ethernet_interface(mock_platform_system, logger):
    return Ethernet(logger)


class TestEthernet:
    @patch('platform.system', return_value='Linux')
    def test_detect_os_linux(self, mock_platform_system, logger):
        interface = Ethernet(logger)
        assert interface.os_info == 'linux'

    @patch('platform.system', return_value='Windows')
    def test_detect_os_windows(self, mock_platform_system, logger):
        interface = Ethernet(logger)
        assert interface.os_info == 'windows'

    @patch('platform.system', return_value='UnsupportedOS')
    def test_detect_os_unsupported(self, mock_platform_system, logger):
        interface = Ethernet(logger)
        assert interface.os_info == 'unsupported'
        interface.logger.error.assert_called_with('Unsupported OS: UnsupportedOS')

    @patch('subprocess.run')
    @patch('platform.system', return_value='Linux')
    def test_detect_success(self, mock_platform_system, mock_subprocess_run, logger):
        mock_subprocess_run.return_value = MagicMock(
            stdout='2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP mode DEFAULT group default qlen 1000',
            stderr='')
        interface = Ethernet(logger)
        devices = interface.detect()
        assert devices == [{'interface': 'eth0', 'description': 'Ethernet Interface'}]
        interface.logger.debug.assert_any_call('Executing command: ip link')
        interface.logger.debug.assert_any_call(
            'Command output: 2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP mode DEFAULT group default qlen 1000')
        interface.logger.debug.assert_any_call('Command stderr: ')

    @patch('subprocess.run')
    @patch('platform.system', return_value='Linux')
    def test_detect_failure(self, mock_platform_system, mock_subprocess_run, logger):
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=['ip', 'link'], output='error', stderr='error'
        )
        interface = Ethernet(logger)
        with pytest.raises(subprocess.CalledProcessError):
            interface.detect()
        interface.logger.error.assert_any_call(
            "Command 'ip link' failed with error: Command '['ip', 'link']' returned non-zero exit status 1.")
        interface.logger.error.assert_any_call('Command stdout: error')
        interface.logger.error.assert_any_call('Command stderr: error')

    @patch('platform.system', return_value='Linux')
    def test_get_command_linux(self, mock_platform_system, logger):
        interface = Ethernet(logger)
        command = interface._get_command('list')
        assert command == ['ip', 'link']

    @patch('platform.system', return_value='Windows')
    def test_get_command_windows(self, mock_platform_system, logger):
        interface = Ethernet(logger)
        command = interface._get_command('list')
        assert command == ['powershell',
                           'Get-NetAdapter -InterfaceDescription *Ethernet* | Format-Table -AutoSize '
                           '-Wrap']

    @patch('platform.system', return_value='Darwin')
    def test_get_command_darwin(self, mock_platform_system, logger):
        interface = Ethernet(logger)
        command = interface._get_command('list')
        assert command == ['networksetup', '-listallhardwareports']

    def test_parse_output_linux(self, logger):
        interface = Ethernet(logger)
        interface.os_info = 'linux'
        output = "2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP mode DEFAULT group default qlen 1000\n3: eth1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP mode DEFAULT group default qlen 1000"
        parsed = interface._parse_output(output)
        assert parsed == [
            {'interface': 'eth0', 'description': 'Ethernet Interface'},
            {'interface': 'eth1', 'description': 'Ethernet Interface'}
        ]

    def test_parse_output_windows(self, logger):
        interface = Ethernet(logger)
        interface.os_info = 'windows'
        output = "Name                      InterfaceDescription                 ifIndex Status       MacAddress         LinkSpeed\n" \
                 "----                      --------------------                 ------- ------       ----------         ---------\n" \
                 "Ethernet                 Ethernet 1                           2       Up           AA:BB:CC:DD:EE:FF  1 Gbps"
        parsed = interface._parse_output(output)
        assert parsed == [
            {'interface': 'Ethernet', 'description': 'Ethernet Interface'}
        ]

    def test_parse_output_darwin(self, logger):
        interface = Ethernet(logger)
        interface.os_info = 'darwin'
        output = "Hardware Port: Ethernet\nDevice: en0\nEthernet Address: AA:BB:CC:DD:EE:FF\n\nHardware Port: Ethernet\nDevice: en1\nEthernet Address: 11:22:33:44:55:66"
        parsed = interface._parse_output(output)
        assert parsed == [
            {'interface': 'en0', 'description': 'Ethernet Interface'},
            {'interface': 'en1', 'description': 'Ethernet Interface'}
        ]

    def test_parse_output_empty(self, logger):
        interface = Ethernet(logger)
        interface.os_info = 'windows'
        output = ""
        parsed = interface._parse_output(output)
        assert parsed == []

    @patch('platform.system', return_value='Linux')
    def test_get_ip_configuration_linux(self, mock_platform_system, logger):
        interface = Ethernet(logger)
        device_identifier = 'eth0'
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout='inet 192.168.1.2 netmask 255.255.255.0 broadcast 192.168.1.255',
                                              stderr='')
            ip_config = interface.get_ip_configuration(device_identifier)
            assert ip_config == {'ip_address': '192.168.1.2', 'netmask': '255.255.255.0', 'broadcast': '192.168.1.255'}
            mock_run.assert_called_with(['ip', 'addr', 'show', device_identifier], capture_output=True, text=True,
                                        shell=False, check=True)

    @patch('platform.system', return_value='Windows')
    def test_get_ip_configuration_windows(self, mock_platform_system, logger):
        interface = Ethernet(logger)
        device_identifier = 'Ethernet'
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                stdout='IPv4 Address. . . . . . . . . . . : 192.168.1.2\nSubnet Mask . . . . . . . . . . . : 255.255.255.0\nDefault Gateway . . . . . . . . . : 192.168.1.1',
                stderr='')
            ip_config = interface.get_ip_configuration(device_identifier)
            assert ip_config == {'ip_address': '192.168.1.2', 'netmask': '255.255.255.0', 'gateway': '192.168.1.1'}
            mock_run.assert_called_with(['powershell', f'Get-NetIPAddress -InterfaceAlias {device_identifier}'],
                                        capture_output=True, text=True, shell=True, check=True)

    @patch('platform.system', return_value='Darwin')
    def test_get_ip_configuration_darwin(self, mock_platform_system, logger):
        interface = Ethernet(logger)
        device_identifier = 'en0'
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout='inet 192.168.1.2 netmask 0xffffff00 broadcast 192.168.1.255',
                                              stderr='')
            ip_config = interface.get_ip_configuration(device_identifier)
            assert ip_config == {'ip_address': '192.168.1.2', 'netmask': '0xffffff00', 'broadcast': '192.168.1.255'}
            mock_run.assert_called_with(['ifconfig', device_identifier], capture_output=True, text=True, shell=False,
                                        check=True)

    @patch('socket.socket')
    def test_send_data(self, mock_socket, logger):
        interface = Ethernet(logger)
        mock_socket_inst = mock_socket.return_value.__enter__.return_value
        interface.send_data('192.168.1.2', 8080, 'test data')
        mock_socket_inst.connect.assert_called_with(('192.168.1.2', 8080))
        mock_socket_inst.sendall.assert_called_with(b'test data')

    @patch('socket.socket')
    def test_receive_data(self, mock_socket, logger):
        interface = Ethernet(logger)
        mock_socket_inst = mock_socket.return_value.__enter__.return_value
        mock_conn = MagicMock()
        mock_socket_inst.accept.return_value = (mock_conn, ('192.168.1.2', 8080))
        mock_conn.recv.return_value = b'test data'
        data = interface.receive_data(8080)
        assert data == 'test data'
        mock_socket_inst.bind.assert_called_with(('', 8080))
        mock_socket_inst.listen.assert_called_once()
        mock_socket_inst.accept.assert_called_once()
        mock_conn.recv.assert_called_with(1024)

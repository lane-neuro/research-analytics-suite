import pytest
from unittest import mock
import platform
import subprocess

from research_analytics_suite.hardware_manager.interface.network import EthernetDetector


class TestEthernetDetector:
    @pytest.fixture
    def logger(self):
        with mock.patch('research_analytics_suite.utils.CustomLogger') as logger:
            yield logger

    def test_detect_ethernet_linux_success(self, logger):
        with mock.patch('platform.system', return_value='linux'):
            ethernet_detector = EthernetDetector(logger)
            ip_link_output = "2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP mode DEFAULT group default qlen 1000\n"
            expected_result = ["2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500"]

            with mock.patch('subprocess.run', return_value=mock.Mock(stdout=ip_link_output, returncode=0)):
                result = ethernet_detector.detect_ethernet()
                assert result == expected_result
                logger.info.assert_any_call("Detecting Ethernet connections...")
                logger.info.assert_any_call(f"Detected Ethernet connections: {expected_result}")

    def test_detect_ethernet_windows_success(self, logger):
        with mock.patch('platform.system', return_value='windows'):
            ethernet_detector = EthernetDetector(logger)
            powershell_output = "Name                      : Ethernet\nStatus                    : Up\n"
            expected_result = ["Name                      : Ethernet", "Status                    : Up"]

            with mock.patch('subprocess.run', return_value=mock.Mock(stdout=powershell_output, returncode=0)):
                result = ethernet_detector.detect_ethernet()
                assert result == expected_result
                logger.info.assert_any_call("Detecting Ethernet connections...")
                logger.info.assert_any_call(f"Detected Ethernet connections: {expected_result}")

    def test_detect_ethernet_macos_success(self, logger):
        with mock.patch('platform.system', return_value='darwin'):
            ethernet_detector = EthernetDetector(logger)
            ifconfig_output = "en0: flags=8863<UP,BROADCAST,SMART,RUNNING,SIMPLEX,MULTICAST> mtu 1500\n\tstatus: active\n"
            expected_result = ["en0: flags=8863<UP,BROADCAST,SMART,RUNNING,SIMPLEX,MULTICAST> mtu 1500"]

            with mock.patch('subprocess.run', return_value=mock.Mock(stdout=ifconfig_output, returncode=0)):
                result = ethernet_detector.detect_ethernet()
                assert result == expected_result
                logger.info.assert_any_call("Detecting Ethernet connections...")
                logger.info.assert_any_call(f"Detected Ethernet connections: {expected_result}")

    def test_read_ethernet_data_linux(self, logger):
        with mock.patch('platform.system', return_value='linux'):
            ethernet_detector = EthernetDetector(logger)
            proc_net_output = "Inter-|   Receive                                                |  Transmit\n"
            expected_result = proc_net_output

            with mock.patch('subprocess.run', return_value=mock.Mock(stdout=proc_net_output, returncode=0)):
                result = ethernet_detector.read_ethernet_data()
                assert result == expected_result
                logger.info.assert_any_call("Reading data from Ethernet connection...")
                logger.info.assert_any_call("Data read from Ethernet connection.")

    def test_read_ethernet_data_windows(self, logger):
        with mock.patch('platform.system', return_value='windows'):
            ethernet_detector = EthernetDetector(logger)
            powershell_output = "ReceivedBytes   : 123456\nSentBytes       : 654321\n"
            expected_result = powershell_output

            with mock.patch('subprocess.run', return_value=mock.Mock(stdout=powershell_output, returncode=0)):
                result = ethernet_detector.read_ethernet_data()
                assert result == expected_result
                logger.info.assert_any_call("Reading data from Ethernet connection...")
                logger.info.assert_any_call("Data read from Ethernet connection.")

    def test_read_ethernet_data_macos(self, logger):
        with mock.patch('platform.system', return_value='darwin'):
            ethernet_detector = EthernetDetector(logger)
            netstat_output = "Name  Mtu   Network       Address            Ipkts  Ierrs Opkts  Oerrs  Coll\n"
            expected_result = netstat_output

            with mock.patch('subprocess.run', return_value=mock.Mock(stdout=netstat_output, returncode=0)):
                result = ethernet_detector.read_ethernet_data()
                assert result == expected_result
                logger.info.assert_any_call("Reading data from Ethernet connection...")
                logger.info.assert_any_call("Data read from Ethernet connection.")

    def test_transmit_ethernet_data_linux(self, logger):
        with mock.patch('platform.system', return_value='linux'):
            ethernet_detector = EthernetDetector(logger)
            data = "Test data"
            with mock.patch('subprocess.run', return_value=mock.Mock(returncode=0)):
                result = ethernet_detector.transmit_ethernet_data(data)
                assert result is True
                logger.info.assert_any_call("Transmitting data over Ethernet connection...")
                logger.info.assert_any_call("Data transmitted over Ethernet connection.")

    def test_transmit_ethernet_data_windows(self, logger):
        with mock.patch('platform.system', return_value='windows'):
            ethernet_detector = EthernetDetector(logger)
            data = "Test data"
            with mock.patch('subprocess.run', return_value=mock.Mock(returncode=0)):
                result = ethernet_detector.transmit_ethernet_data(data)
                assert result is True
                logger.info.assert_any_call("Transmitting data over Ethernet connection...")
                logger.info.assert_any_call("Data transmitted over Ethernet connection.")

    def test_transmit_ethernet_data_macos(self, logger):
        with mock.patch('platform.system', return_value='darwin'):
            ethernet_detector = EthernetDetector(logger)
            data = "Test data"
            with mock.patch('subprocess.run', return_value=mock.Mock(returncode=0)):
                result = ethernet_detector.transmit_ethernet_data(data)
                assert result is True
                logger.info.assert_any_call("Transmitting data over Ethernet connection...")
                logger.info.assert_any_call("Data transmitted over Ethernet connection.")

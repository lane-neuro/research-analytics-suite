import pytest
from unittest import mock
from research_analytics_suite.hardware_manager.cpu.CPUInstaller import CPUInstaller
from research_analytics_suite.hardware_manager.cpu.CPUDetector import CPUDetector


class TestCPUInstaller:
    @pytest.fixture
    def logger(self):
        with mock.patch('research_analytics_suite.utils.CustomLogger') as logger:
            yield logger

    @pytest.fixture
    def remote_manager(self):
        return mock.Mock()

    @pytest.fixture
    def cpu_installer(self, logger, remote_manager):
        return CPUInstaller(logger, remote_manager)

    def test_initialization(self, cpu_installer, logger, remote_manager):
        assert cpu_installer.logger == logger
        assert cpu_installer.remote_manager == remote_manager
        assert isinstance(cpu_installer.cpu_detector, CPUDetector)
        assert cpu_installer.remote_servers == []

    def test_initialization_with_remote_servers(self, logger, remote_manager):
        remote_servers = ["server1", "server2"]
        cpu_installer = CPUInstaller(logger, remote_manager, remote_servers)
        assert cpu_installer.logger == logger
        assert cpu_installer.remote_manager == remote_manager
        assert isinstance(cpu_installer.cpu_detector, CPUDetector)
        assert cpu_installer.remote_servers == remote_servers

    def test_install_no_cpus_detected(self, cpu_installer, logger):
        with mock.patch.object(cpu_installer.cpu_detector, 'detect_cpus', return_value=[]):
            result = cpu_installer.install()
            assert result == []
            logger.error.assert_called_with("No CPUs detected.")

    def test_install_with_cpus_detected(self, cpu_installer, logger):
        detected_cpus = [{
            "physical_cores": 4,
            "logical_cores": 8,
            "architecture": 'x86_64'
        }]
        with mock.patch.object(cpu_installer.cpu_detector, 'detect_cpus', return_value=detected_cpus):
            result = cpu_installer.install()
            assert result == detected_cpus
            logger.info.assert_called_with(f"Detected CPUs: {detected_cpus}")

    def test_install_with_remote_servers(self, cpu_installer, logger, remote_manager):
        detected_cpus = [{
            "physical_cores": 4,
            "logical_cores": 8,
            "architecture": 'x86_64'
        }]
        remote_servers = ["server1", "server2"]
        cpu_installer.remote_servers = remote_servers

        with mock.patch.object(cpu_installer.cpu_detector, 'detect_cpus', return_value=detected_cpus):
            result = cpu_installer.install()
            assert result == detected_cpus
            logger.info.assert_called_with(f"Detected CPUs: {detected_cpus}")
            for server in remote_servers:
                remote_manager.manage_remote_cpu_server.assert_any_call(server)

    def test_install_with_empty_remote_servers(self, cpu_installer, logger, remote_manager):
        detected_cpus = [{
            "physical_cores": 4,
            "logical_cores": 8,
            "architecture": 'x86_64'
        }]
        cpu_installer.remote_servers = []

        with mock.patch.object(cpu_installer.cpu_detector, 'detect_cpus', return_value=detected_cpus):
            result = cpu_installer.install()
            assert result == detected_cpus
            logger.info.assert_called_with(f"Detected CPUs: {detected_cpus}")
            remote_manager.manage_remote_cpu_server.assert_not_called()

    def test_install_exception_during_cpu_detection(self, cpu_installer, logger):
        with mock.patch.object(cpu_installer.cpu_detector, 'detect_cpus', side_effect=Exception("Detection error")):
            result = cpu_installer.install()
            assert result == []
            logger.error.assert_called_with("Error during CPU detection: Detection error")

    def test_install_exception_during_remote_management(self, cpu_installer, logger, remote_manager):
        detected_cpus = [{
            "physical_cores": 4,
            "logical_cores": 8,
            "architecture": 'x86_64'
        }]
        remote_servers = ["server1", "server2"]
        cpu_installer.remote_servers = remote_servers

        with mock.patch.object(cpu_installer.cpu_detector, 'detect_cpus', return_value=detected_cpus):
            with mock.patch.object(remote_manager, 'manage_remote_cpu_server', side_effect=Exception("Remote management error")):
                result = cpu_installer.install()
                assert result == detected_cpus
                logger.info.assert_called_with(f"Detected CPUs: {detected_cpus}")
                calls = [
                    mock.call(f"Error managing remote server server1: Remote management error"),
                    mock.call(f"Error managing remote server server2: Remote management error")
                ]
                logger.error.assert_has_calls(calls, any_order=True)

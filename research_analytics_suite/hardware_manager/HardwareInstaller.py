"""
Hardware Installer

This module contains the HardwareInstaller class, which orchestrates the hardware detection,
installation, benchmarking, and status checking processes.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
from .TaskManager import TaskManager
from .RemoteManager import RemoteManager
from .gpu.GPUInstaller import GPUInstaller
from .cpu.CPUInstaller import CPUInstaller
from .benchmark import BenchmarkManager
from .interface import InterfaceManager
from .system_info.MemoryInfo import MemoryInfo
from .system_info.StorageInfo import StorageInfo
from .system_info.NetworkInfo import NetworkInfo
from .system_info.BatteryInfo import BatteryInfo
from .system_info.OSInfo import OSInfo
from .system_info.TemperatureInfo import TemperatureInfo
from .system_info.PeripheralsInfo import PeripheralsInfo
from ..utils import CustomLogger


class HardwareInstaller:
    def __init__(self, remote_servers=None):
        self.logger = CustomLogger()
        self.task_manager = TaskManager(self.logger)
        self.remote_manager = RemoteManager(self.logger, remote_servers)
        self.benchmark_manager = BenchmarkManager(self.logger)
        self.interface_manager = InterfaceManager(self.logger)

        self.memory_info = MemoryInfo(self.logger)
        self.storage_info = StorageInfo(self.logger)
        self.network_info = NetworkInfo(self.logger)
        self.battery_info = BatteryInfo(self.logger)
        self.os_info = OSInfo(self.logger)
        self.temperature_info = TemperatureInfo(self.logger)
        self.peripherals_info = PeripheralsInfo(self.logger)

        self.gpu_installer = GPUInstaller(self.logger, self.remote_manager, remote_servers)
        self.cpu_installer = CPUInstaller(self.logger, self.remote_manager, remote_servers)

    def install(self):
        """Detect hardware, manage installations and tasks, run benchmarks, and gather system information."""
        gpu_info = self.gpu_installer.install()
        cpu_info = self.cpu_installer.install()

        hardware_info = {
            'cpu': cpu_info,
            'gpu': gpu_info
        }
        self.logger.info(f"Detected hardware: {hardware_info}")

        for server in self.remote_manager.remote_servers:
            self.remote_manager.manage_remote_server(server)

        self.task_manager.manage_tasks(hardware_info)

        benchmark_results = self.benchmark_manager.run_benchmarks(hardware_info['cpu'], hardware_info['gpu'])
        self.logger.info(f"Benchmark results: {benchmark_results}")

        memory_info = self.memory_info.get_memory_info()
        storage_info = self.storage_info.get_storage_info()
        network_info = self.network_info.get_network_info()
        battery_info = self.battery_info.get_battery_info()
        os_info = self.os_info.get_os_info()
        temperature_info = self.temperature_info.get_temperature_info()
        peripherals_info = self.peripherals_info.get_peripherals_info()

        system_info = {
            "memory_info": memory_info,
            "storage_info": storage_info,
            "network_info": network_info,
            "battery_info": battery_info,
            "os_info": os_info,
            "temperature_info": temperature_info,
            "peripherals_info": peripherals_info
        }
        self.logger.info(f"System information: {system_info}")

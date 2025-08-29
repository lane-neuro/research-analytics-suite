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
from .gpu.GPUManager import GPUManager
from .cpu.CPUManager import CPUManager
# from .benchmark import BenchmarkManager
from .interface.InterfaceManager import InterfaceManager
from .system_info.MemoryInfo import MemoryInfo
from .system_info.StorageInfo import StorageInfo
from .system_info.NetworkInfo import NetworkInfo
from .system_info.BatteryInfo import BatteryInfo
from .system_info.OSInfo import OSInfo
from .system_info.TemperatureInfo import TemperatureInfo
from .system_info.PeripheralsInfo import PeripheralsInfo
from research_analytics_suite.utils import CustomLogger
from .utils import _to_gib


class HardwareManager:
    def __init__(self, remote_servers=None):
        self.logger = CustomLogger()
        self.task_manager = TaskManager(self.logger)
        self.remote_manager = RemoteManager(self.logger, remote_servers)
        self.interface_manager = InterfaceManager()
        # self.benchmark_manager = BenchmarkManager(self.logger, self.interface_manager)

        self.memory_info = MemoryInfo(self.logger)
        self.storage_info = StorageInfo(self.logger)
        self.network_info = NetworkInfo(self.logger)
        self.battery_info = BatteryInfo(self.logger)
        self.os_info = OSInfo(self.logger)
        # self.temperature_info = TemperatureInfo(self.logger)
        # self.peripherals_info = PeripheralsInfo(self.logger)

        self.gpu_mgr = GPUManager(self.logger, self.remote_manager, remote_servers)
        self.cpu_mgr = CPUManager(self.logger, self.remote_manager, remote_servers)

    def detect(self):
        """Detect hardware, manage installations and tasks, run benchmarks, and gather system information."""
        self.interface_manager.detect_interfaces()
        gpu_info = self.gpu_mgr.detect_hardware()
        cpu_info = self.cpu_mgr.detect_hardware()

        # for server in self.remote_manager.remote_servers:
        #     self.remote_manager.manage_remote_server(server)

        # self.task_manager.manage_tasks(hardware_info)

        # benchmark_results = self.benchmark_manager.run_benchmarks(hardware_info['cpu'], hardware_info['gpu'])
        # self.logger.info(f"Benchmark results: {benchmark_results}")

        memory_info = self.memory_info.get_memory_info()
        # storage_info = self.storage_info.get_storage_info()
        # network_info = self.network_info.get_network_info()
        # battery_info = self.battery_info.get_battery_info()
        # os_info = self.os_info.get_os_info()
        # temperature_info = self.temperature_info.get_temperature_info()
        # peripherals_info = self.peripherals_info.get_peripherals_info()

        system_info = {
            "memory_info": memory_info,
            "cpu_info": cpu_info,
            "gpu_info": gpu_info,
            # "storage_info": storage_info,
            # "network_info": network_info,
            # "battery_info": battery_info,
            # "os_info": os_info,
            # "temperature_info": temperature_info,
            # "peripherals_info": peripherals_info
        }
        self.logger.debug(f"System information: {system_info}")

    @property
    def ram_size(self):
        """Get the total RAM size, converted to gigabytes and rounded to two decimal places."""
        return round(self.memory_info.total_memory / (1024 ** 3), 2)

    @property
    def gpu_size(self, index: int = 0):
        """Return GPU memory as GiB (rounded to 2 decimals), or 'Unknown GPU Size'."""
        if index < len(self.gpu_mgr.gpus):
            gpu = self.gpu_mgr.gpus[index]
            if 'memory' in gpu:
                try:
                    return round(_to_gib(gpu['memory']), 2)
                except Exception as e:
                    self.logger.warning(f"Unable to parse GPU memory: {gpu.get('memory')!r} ({e})")
        return 'Unknown GPU Size'

    @property
    def cpus(self):
        """Get the list of CPUs."""
        return self.cpu_mgr.cpus

    @property
    def gpus(self):
        """Get the list of GPUs."""
        return self.gpu_mgr.gpus

    @property
    def interfaces(self):
        """Get the detected hardware interfaces."""
        return self.interface_manager.interfaces

    def get_interfaces_by_type(self, interface_type: str) -> list:
        """Get interfaces of a specific type."""
        return self.interface_manager.get_interfaces_by_type(interface_type)


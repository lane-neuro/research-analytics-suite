"""
BenchmarkManager

This module contains the BenchmarkManager class, which manages the running of benchmarks
for CPU and GPU, and checks the status of interfaces.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
from .CPUBenchmark import CPUBenchmark
from .GPUBenchmark import GPUBenchmark
from research_analytics_suite.hardware_manager.interface.InterfaceStatusChecker import InterfaceStatusChecker


class BenchmarkManager:
    def __init__(self, logger, interface_manager):
        self.logger = logger
        self.interface_manager = interface_manager
        self.cpu_benchmark = CPUBenchmark(logger)
        self.gpu_benchmark = GPUBenchmark(logger)
        self.status_checker = InterfaceStatusChecker(logger, self.interface_manager)

    def run_benchmarks(self, cpu_info: list[dict], gpu_info: list[dict]) -> dict:
        """Run benchmarks for CPU and GPU, and check the status of interfaces.

        Args:
            cpu_info (list[dict]): Information about the detected CPUs.
            gpu_info (list[dict]): Information about the detected GPUs.

        Returns:
            dict: Results of the benchmarks and status checks.
        """
        self.logger.info("Running CPU benchmarks...")
        self.cpu_benchmark.run_benchmarks(cpu_info)
        self.logger.info(f"CPU benchmark complete.")

        self.logger.info("Running GPU benchmarks...")
        self.gpu_benchmark.run_benchmarks(gpu_info)
        self.logger.info(f"GPU benchmark complete.")

        self.logger.info("Checking status of all interfaces...")
        status_report = self.status_checker.check_status()
        self.status_checker.print_status_report(status_report)

        return {
            "cpu_info": cpu_info,
            "gpu_info": gpu_info,
            "status_report": status_report
        }

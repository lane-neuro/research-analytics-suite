"""
CPUBenchmark

This module contains the CPUBenchmark class, which runs benchmarks for CPU performance.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import time
import multiprocessing


class CPUBenchmark:
    def __init__(self, logger):
        self.logger = logger

    def cpu_bound_task(self, core):
        """Example CPU-bound task for benchmarking.

        Args:
            core (int): The CPU core to run the task on.

        Returns:
            float: The time taken to complete the task.
        """
        self.logger.info(f"Running benchmark on CPU core {core}")
        start_time = time.time()
        result = sum(i * i for i in range(1000000))
        end_time = time.time()
        return end_time - start_time

    def run_benchmark(self, cpu_info: dict):
        """Run CPU benchmarks.

        Args:
            cpu_info (dict): Information about the detected CPUs.

        Returns:
            list: Results of the CPU benchmarks.
        """
        num_cores = cpu_info['physical_cores']
        with multiprocessing.Pool(num_cores) as pool:
            results = pool.map(self.cpu_bound_task, range(num_cores))
        return results

    def run_benchmarks(self, cpu_dict: list[dict]) -> list[dict]:
        """Run CPU benchmarks.

        Args:
            cpu_dict (list[dict]): Information about the detected CPUs.

        Returns:
            list: Results of the CPU benchmarks.
        """
        for cpu in cpu_dict:
            self.logger.info(f"Running benchmarks for CPU: {cpu['name']}")
            cpu.benchmark = self.run_benchmark(cpu)
            self.logger.info(f"Benchmark results for CPU {cpu['name']}: {cpu.benchmark}")
        return cpu_dict

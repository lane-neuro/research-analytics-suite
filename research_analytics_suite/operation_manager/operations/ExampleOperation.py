"""
Operation: ExampleOperation
Version: 0.0.1
Description: A basic implementation of an operation that calculates the mean and standard deviation of a list of
             numbers.

Author: Lane
GitHub: @lane-neuro
Email: justlane@uw.edu

---
Part of the Research Analytics Suite
License: BSD 3-Clause License
Maintainer: Lane
Status: Template
"""

import statistics
from typing import Any, List
from research_analytics_suite.operation_manager.operations.OperationTemplate import OperationTemplate


class ExampleOperation(OperationTemplate):
    """
    ExampleOperation class extends the OperationTemplate to perform a specific analytical task: calculating the mean
    and standard deviation of a list of numbers.
    
    Example Usage:
    ```python
        numbers = [1, 2, 3, 4, 5]
        operation = ExampleOperation(numbers)
        await operation.initialize_operation()
        await operation.execute()
        result = await operation.get_results_from_memory()
    ```

    Attributes:
        numbers (List[float]): The list of numbers to analyze.

    Methods:
        __init__: Initialize the operation with the list of numbers.
        initialize_operation: Initialize any resources or setup required for the operation.
        execute: Execute the operation's logic.
    """

    name: str = "ExampleOperation"
    persistent: bool = False
    is_cpu_bound: bool = False
    concurrent: bool = False

    def __init__(self, numbers: List[float], *args: Any, **kwargs: Any):
        """
        Initialize the operation with the list of numbers.

        Args:
            numbers (List[float]): The list of numbers to analyze.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self.numbers = numbers
        super().__init__(*args, **kwargs)
        self._action = self.execute

    async def initialize_operation(self):
        """
        Initialize any resources or setup required for the operation before it starts.
        """
        await super().initialize_operation()
        self.add_log_entry("ExampleOperation initialized")

    async def execute(self):
        """
        Execute the operation's logic: calculate the mean and standard deviation of the list of numbers.
        """
        await self.pre_execute()

        self.add_log_entry("ExampleOperation execution started")

        try:
            if not self.numbers:
                raise ValueError("The list of numbers is empty")

            mean_value = statistics.mean(self.numbers)
            std_dev_value = statistics.stdev(self.numbers)

            self._progress = 100
            self._status = "completed"
            self.add_log_entry(f"Mean: {mean_value}, Standard Deviation: {std_dev_value}")
            self.add_log_entry("ExampleOperation execution completed successfully")

        except Exception as e:
            self.handle_error(e)

        await self.post_execute()

    def validate(self):
        """
        Validate the input list of numbers.
        """
        self.add_log_entry("Validation started")
        if not isinstance(self.numbers, list) or not all(isinstance(x, (int, float)) for x in self.numbers):
            raise ValueError("Input should be a list of numbers")
        self.add_log_entry("Validation completed")

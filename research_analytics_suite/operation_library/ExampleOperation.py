"""
Operation:      ExampleOperation
Version:        0.0.1
Description:    A basic implementation of an operation that calculates the mean and standard deviation of a list of
                numbers.

Author:         Lane
GitHub:         @lane-neuro
Email:          justlane@uw.edu

---
Part of the Research Analytics Suite (RAS)
    https://github.com/lane-neuro/research-analytics-suite
License:        BSD 3-Clause License
Maintainer:     Lane (GitHub: @lane-neuro)
Status:         Example
"""
import statistics
from typing import Any, List

from research_analytics_suite.operation_manager import BaseOperation


class ExampleOperation(BaseOperation):
    """
    ExampleOperation class extends the BaseOperation class to provide a concrete implementation of an operation.
    This operation calculates the mean and standard deviation of a list of numbers provided as input.
    
    Example Usage (in a script):
    ```python
        # Create an instance of the operation with a list of numbers
        numbers = [1, 2, 3, 4, 5]
        operation = ExampleOperation(numbers)

        # Initialize the operation
        await operation.initialize_operation()

        # Execute the operation
        await operation.execute()

        # Retrieve the result (dictionary) from memory outputs
        result = await operation.get_results_from_memory()
    ```

    Example Usage (within RAS):
    ```python
        # Create an instance of the operation with a list of numbers
        numbers = [1, 2, 3, 4, 5]
        operation = ExampleOperation(numbers)

        # Add the operation to the operation manager
        await operation_manager.add_operation(operation)
    ```

    Attributes:
        numbers (List[float]): The list of numbers to analyze.

    Methods:
        __init__: Initialize the operation with the list of numbers.
        initialize_operation: Initialize any resources or setup required for the operation.
        execute: Execute the operation's logic.
    """

    category_id: int = 1
    version: str = "0.0.1"
    name: str = "ExampleOperation"
    author: str = "Lane"
    github: str = "lane-neuro"
    email: str = "justlane@uw.edu"
    description: str = ("A basic implementation of an operation that calculates the mean and standard deviation "
                        "of a list of numbers.")
    action: str = "Calculates the mean and standard deviation of a list of numbers."
    persistent: bool = False
    is_cpu_bound: bool = False
    concurrent: bool = False
    dependencies: []
    parent_operation: None
    child_operations: None
    unique_id: str = f"{author}_{name}_{version}"

    def __init__(self, numbers: List[float], *args: Any, **kwargs: Any):
        """
        Initialize the operation with the list of numbers.

        Args:
            numbers (List[float]): The list of numbers to analyze.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        # Update kwargs with attributes
        kwargs.update({
            'unique_id': self.unique_id,
            'category_id': self.category_id,
            'version': self.version,
            'name': self.name,
            'author': self.author,
            'github': self.github,
            'email': self.email,
            'description': self.description,
            'action': self.execute,
            'persistent': self.persistent,
            'is_cpu_bound': self.is_cpu_bound,
            'concurrent': self.concurrent,
            'dependencies': self.dependencies,
            'parent_operation': self.parent_operation,
            'child_operations': self.child_operations,
        })

        # Don't forget to initialize any custom attributes/input parameters
        self.numbers = numbers

        # Call the parent class constructor
        super().__init__(*args, **kwargs)

    async def initialize_operation(self):
        """
        Initialize any resources or setup required for the operation before it starts.
        """
        await super().initialize_operation()
        self.add_log_entry(f"ExampleOperation initialized with numbers: {self.numbers}")

    async def pre_execute(self):
        """
        Logic to run before the main execution.
        """
        self.validate()
        self.add_log_entry("Pre-execution checks completed")

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
            self.add_log_entry(f"Mean: {mean_value}, Standard Deviation: {std_dev_value}")

        except Exception as e:
            self.handle_error(e)

        await self.post_execute()

    async def post_execute(self):
        """
        Logic to run after the main execution.
        """
        try:
            self.validate()
            self._progress = 100
            self._status = "completed"
            self.add_log_entry("OperationTemplate completed.")
        except Exception as e:
            self.handle_error(e)

    def validate(self):
        """
        Validate the input list of numbers.
        """
        self.add_log_entry("Validation started")
        if not isinstance(self.numbers, list) or not all(isinstance(x, (int, float)) for x in self.numbers):
            raise ValueError("Input should be a list of numbers")
        self.add_log_entry("Validation completed")

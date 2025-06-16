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
from typing import List
from research_analytics_suite.operation_manager import BaseOperation


class ExampleOperation(BaseOperation):
    """
    A basic implementation of an operation that calculates the mean and standard deviation of a list of numbers.

    Returns:
        mean_value (float): The mean of the numbers.
        std_dev_value (float): The standard deviation of the numbers.
    """

    name: str = "ExampleOperation"                      # Name of the operation
    version: str = "0.0.1"                              # Version of the operation
    description: str = ("A basic implementation of an operation that calculates the mean and standard deviation "
                        "of a list of numbers.")        # Description of the operation
    category_id: int = -1                               # Category ID for the operation
    author: str = "Lane"                                # Author of the operation
    github: str = "lane-neuro"                          # GitHub username of the author
    email: str = "justlane@uw.edu"                      # Email address of the author
    unique_id: str = f"{github}_{name}_{version}"       # Unique ID for the operation
    required_inputs: dict = {"numbers": List[int]}      # dict[str, type] of required input parameters
    parent_operation: BaseOperation = None              # Parent operation class
    inheritance: list = []                              # list of unique IDs of child operations
    is_loop: bool = False                               # Flag to indicate if the operation is a loop
    is_cpu_bound: bool = False                          # Flag to indicate if the operation is CPU-bound
    parallel: bool = False                              # Flag to indicate if the operation can run in parallel

    def __init__(self, *args, **kwargs):
        """
        Initialize the operation with the list of numbers.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        # Call the parent class constructor
        super().__init__(*args, **kwargs)

    async def initialize_operation(self):
        """
        Initialize any resources or setup required for the operation before it starts.
        """
        await super().initialize_operation()
        self.add_log_entry(f"ExampleOperation initialized")

    async def pre_execute(self, _numbers: List[int]):
        """
        Logic to run before the main execution.
        """
        self.validate(_numbers)
        self.add_log_entry("Pre-execution checks completed")

    async def execute(self):
        """
        Execute the operation's logic: calculate the mean and standard deviation of the list of numbers.
        """
        inputs = self.get_inputs()
        _numbers = inputs.get("numbers", [])
        mean_value = 0
        std_dev_value = 0

        await self.pre_execute(_numbers)

        self.add_log_entry("ExampleOperation execution started")

        try:
            mean_value = statistics.mean(_numbers)
            std_dev_value = statistics.stdev(_numbers)
            self.add_log_entry(f"Mean: {mean_value}, Standard Deviation: {std_dev_value}")

        except Exception as e:
            self.handle_error(e)

        await self.post_execute()

        return {"mean": mean_value, "std_dev": std_dev_value}

    async def post_execute(self):
        """
        Logic to run after the main execution.
        """
        try:
            self.validate()
            self._progress = 100
            self._status = "completed"
            self.add_log_entry("ExampleOperation completed.")
        except Exception as e:
            self.handle_error(e)

    def validate(self, _numbers: List[int] = None):
        """
        Validate the input list of numbers.
        """
        self.add_log_entry("Validation started")
        if not isinstance(_numbers, list) or not all(isinstance(x, (int, float)) for x in _numbers):
            raise ValueError("Input should be a list of numbers")
        self.add_log_entry("Validation completed")

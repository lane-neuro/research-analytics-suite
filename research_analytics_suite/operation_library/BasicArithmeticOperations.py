"""
Operation:      BasicArithmeticOperations
Version:        0.0.1
Description:    Perform basic arithmetic operations on data.

Author:         Lane
GitHub:         lane-neuro
Email:          justlane@uw.edu

---
Part of the Research Analytics Suite
    https://github.com/lane-neuro/research-analytics-suite
License:        BSD 3-Clause License
Maintainer:     Lane (GitHub: @lane-neuro)
Status:         In Progress
"""
from typing import List, Optional, Type
from research_analytics_suite.operation_manager import BaseOperation


class BasicArithmeticOperations(BaseOperation):
    """
    Perform basic arithmetic operations on data.

    Attributes:
        numbers (List[float]): The list of numbers to perform arithmetic operations on.

    Returns:
        total (float): The sum of the numbers.
        average (float): The average of the numbers.
    """
    name = "BasicArithmeticOperations"
    version = "0.0.1"
    description = "Perform basic arithmetic operations on data."
    category_id = 1102
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    unique_id = f"{github}_{name}_{version}"
    required_inputs = {"numbers": list}
    parent_operation: Optional[Type[BaseOperation]] = None
    inheritance: Optional[list] = []
    is_loop = False
    is_cpu_bound = False
    parallel = False

    def __init__(self, numbers: List[float], *args, **kwargs):
        """
        Initialize the operation with the list of numbers.

        Args:
            numbers (List[float]): The list of numbers to perform arithmetic operations on.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self.numbers = numbers
        super().__init__(*args, **kwargs)

    async def initialize_operation(self):
        """
        Initialize any resources or setup required for the operation before it starts.
        """
        await super().initialize_operation()

    async def execute(self):
        """
        Execute the operation's logic: perform basic arithmetic operations on the numbers.
        """
        total = sum(self.numbers)
        average = total / len(self.numbers)
        print(f"Total: {total}, Average: {average}")

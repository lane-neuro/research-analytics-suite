"""
Operation:      TrainTestSplit
Version:        0.0.1
Description:    Split a dataset into training and testing sets.

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
from typing import List, Tuple, Optional, Type
from sklearn.model_selection import train_test_split
from research_analytics_suite.operation_manager import BaseOperation


class TrainTestSplit(BaseOperation):
    """
    Split a dataset into training and testing sets.

    Attributes:
        x (List): The features.
        y (List): The target variable.
        test_size (float): The proportion of the dataset to include in the test split.

    Returns:
        x_train (List): The training set features.
        x_test (List): The testing set features.
        y_train (List): The training set target variable.
        y_test (List): The testing set target variable
    """
    name = "TrainTestSplit"
    version = "0.0.1"
    description = "Split a dataset into training and testing sets."
    category_id = 1301
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    unique_id = f"{github}_{name}_{version}"
    required_inputs = {"X": list, "y": list, "test_size": float}
    parent_operation: Optional[Type[BaseOperation]] = None
    inheritance: Optional[list] = []
    is_loop = False
    is_cpu_bound = False
    parallel = False

    def __init__(self, x: List, y: List, test_size: float, *args, **kwargs):
        """
        Initialize the operation with the features, target variable, and test size.

        Args:
            x (List): The features.
            y (List): The target variable.
            test_size (float): The proportion of the dataset to include in the test split.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self.x = x
        self.y = y
        self.test_size = test_size
        super().__init__(*args, **kwargs)

    async def initialize_operation(self):
        """
        Initialize any resources or setup required for the operation before it starts.
        """
        await super().initialize_operation()

    async def execute(self):
        """
        Execute the operation's logic: split the dataset into training and testing sets.
        """
        x_train, x_test, y_train, y_test = train_test_split(self.x, self.y, test_size=self.test_size)
        print(f"Training set: {x_train}, {y_train}")
        print(f"Testing set: {x_test}, {y_test}")

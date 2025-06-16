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

    Requires:
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
    required_inputs = {"x": list, "y": list, "test_size": float}
    parent_operation: Optional[Type[BaseOperation]] = None
    inheritance: Optional[list] = []
    is_loop = False
    is_cpu_bound = False
    parallel = False

    def __init__(self, *args, **kwargs):
        """
        Initialize the operation.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
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
        _inputs = self.get_inputs()
        _x = _inputs.get("x", [])
        _y = _inputs.get("y", [])
        _test_size = _inputs.get("test_size", 0.2)

        x_train, x_test, y_train, y_test = train_test_split(_x, _y, test_size=_test_size, random_state=42)
        self.add_log_entry(f"[RESULT] Dataset split into (reproducible) training and testing sets.")
        return {
            "x_train": x_train,
            "x_test": x_test,
            "y_train": y_train,
            "y_test": y_test
        }

"""
Operation:      RegressionAnalysis
Version:        0.0.1
Description:    Perform regression analysis on a dataset.

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
import statsmodels.api as sm
from typing import Optional, Type
from research_analytics_suite.operation_manager import BaseOperation


class RegressionAnalysis(BaseOperation):
    """
    Perform regression analysis on a dataset.

    Attributes:
        y (list): The dependent variable.
        x (list): The independent variables.

    Returns:
        x_with_const (list): The independent variables with a constant added.
        model (statsmodels.regression.linear_model.RegressionResultsWrapper): The regression model.
    """
    name = "RegressionAnalysis"
    version = "0.0.1"
    description = "Perform regression analysis on a dataset."
    category_id = 1202
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    unique_id = f"{github}_{name}_{version}"
    required_inputs = {"y": list, "x": list}
    parent_operation: Optional[Type[BaseOperation]] = None
    inheritance: Optional[list] = []
    is_loop = False
    is_cpu_bound = False
    parallel = False

    def __init__(self, y: list, x: list, *args, **kwargs):
        """
        Initialize the operation with the dependent and independent variables.

        Args:
            y (list): The dependent variable.
            x (list): The independent variables.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self.y = y
        self.x = x
        super().__init__(*args, **kwargs)

    async def initialize_operation(self):
        """
        Initialize any resources or setup required for the operation before it starts.
        """
        await super().initialize_operation()

    async def execute(self):
        """
        Execute the operation's logic: perform regression analysis on the dataset.
        """
        x_with_const = sm.add_constant(self.x)
        model = sm.OLS(self.y, x_with_const).fit()
        print(model.summary())

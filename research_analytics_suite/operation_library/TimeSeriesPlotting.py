"""
Operation:      TimeSeriesPlotting
Version:        0.0.1
Description:    Plot a time series.

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
import matplotlib.pyplot as plt
from typing import List, Optional, Type
from research_analytics_suite.operation_manager import BaseOperation


class TimeSeriesPlotting(BaseOperation):
    """
    Plot a time series.

    Attributes:
        time_series (List[float]): The time series data to plot.

    Returns:
        plt: The time series plot.
    """
    name = "TimeSeriesPlotting"
    version = "0.0.1"
    description = "Plot a time series."
    category_id = 401
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    unique_id = f"{github}_{name}_{version}"
    required_inputs = {"time_series": list}
    parent_operation: Optional[Type[BaseOperation]] = None
    inheritance: Optional[list] = []
    is_loop = False
    is_cpu_bound = False
    parallel = False

    def __init__(self, time_series: List[float], *args, **kwargs):
        """
        Initialize the operation with the time series data.

        Args:
            time_series (List[float]): The time series data to plot.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self.time_series = time_series
        super().__init__(*args, **kwargs)

    async def initialize_operation(self):
        """
        Initialize any resources or setup required for the operation before it starts.
        """
        await super().initialize_operation()

    async def execute(self):
        """
        Execute the operation's logic: plot the time series data.
        """
        plt.plot(self.time_series)
        plt.title("Time Series Plot")
        plt.xlabel("Time")
        plt.ylabel("Value")
        plt.show()

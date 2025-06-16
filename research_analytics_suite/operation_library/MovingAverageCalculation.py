"""
Operation:      MovingAverageCalculation
Version:        0.0.1
Description:    Calculate the moving average of a time series.

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


class MovingAverageCalculation(BaseOperation):
    """
    Calculate the moving average of a time series.

    Requires:
        time_series (List[float]): The time series data to calculate the moving average.
        window_size (int): The size of the moving window.

    Returns:
        moving_averages (List[float]): The moving averages of the time series data.
    """
    name = "MovingAverageCalculation"
    version = "0.0.1"
    description = "Calculate the moving average of a time series."
    category_id = 401
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"time_series": list, "window_size": int}
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
        Execute the operation's logic: calculate the moving average of the time series data.
        """
        _inputs = self.get_inputs()
        time_series = _inputs.get("time_series", [])
        window_size = _inputs.get("window_size", 1)

        moving_averages = []
        for i in range(len(time_series) - window_size + 1):
            this_window = time_series[i : i + window_size]
            window_average = sum(this_window) / window_size
            moving_averages.append(window_average)

        self.add_log_entry(f"[RESULT] Moving Averages: {moving_averages}")
        return {"moving_averages": moving_averages}

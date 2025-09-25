"""
Operation:      HistogramCalculation
Version:        0.0.1
Description:    Generate histogram bins and frequencies for a numerical list.

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
from typing import Optional, Type, Union
import numpy as np
from research_analytics_suite.operation_manager import BaseOperation


class HistogramCalculation(BaseOperation):
    """
    Generate histogram bins and frequencies for a numerical list.

    Requires:
        numbers (list): A list of numerical values to create histogram from.
        bins (int or str): Number of bins or binning strategy (default: 'auto').

    Returns:
        frequencies (list): The frequency count for each bin.
        bin_edges (list): The edges of the bins.
        bin_centers (list): The center points of each bin.
        total_count (int): Total number of data points.
    """
    name = "HistogramCalculation"
    version = "0.0.1"
    description = "Generate histogram bins and frequencies for a numerical list."
    category_id = 103
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"numbers": list, "bins": int}
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
        Execute the operation to generate histogram for the provided numbers.
        """
        _inputs = self.get_inputs()
        _numbers = _inputs.get("numbers", [])
        _bins = _inputs.get("bins", 2)

        if _numbers is None or len(_numbers) == 0:
            raise ValueError("Cannot create histogram of empty list")

        frequencies, bin_edges = np.histogram(_numbers, bins=_bins)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        total_count = len(_numbers)

        self.add_log_entry(f"[RESULT] Histogram created with {len(frequencies)} bins, total count: {total_count}")
        return {
            "frequencies": frequencies.tolist(),
            "bin_edges": bin_edges.tolist(),
            "bin_centers": bin_centers.tolist(),
            "total_count": total_count
        }
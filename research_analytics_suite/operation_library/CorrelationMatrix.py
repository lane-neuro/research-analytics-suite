"""
Operation:      CorrelationMatrix
Version:        0.0.1
Description:    Compute the pairwise Pearson correlation matrix for a set of numeric columns.

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
from typing import Optional, Type
from research_analytics_suite.operation_manager import BaseOperation


class CorrelationMatrix(BaseOperation):
    """
    Compute the pairwise Pearson correlation matrix for a set of numeric columns.

    Requires:
        data (list): A list of equal-length numeric lists (each inner list is one variable).
        labels (list): Column labels for the variables (same order as data).

    Returns:
        correlation_matrix (DataFrame): Labeled correlation matrix with labels as both index and columns.
    """
    name = "CorrelationMatrix"
    version = "0.0.1"
    description = "Compute the pairwise Pearson correlation matrix."
    category_id = 403
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"data": list, "labels": list}
    parent_operation: Optional[Type[BaseOperation]] = None
    inheritance: Optional[list] = []
    is_loop = False
    is_cpu_bound = False
    parallel = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def initialize_operation(self):
        await super().initialize_operation()

    async def execute(self):
        import numpy as np
        import pandas as pd
        _inputs = self.get_inputs()
        data = _inputs.get("data", [])
        labels = _inputs.get("labels", [])

        arr = np.array(data)
        # If shape is (observations x variables), i.e. rows != len(labels), transpose so
        # corrcoef sees rows as variables.
        if arr.ndim == 2 and arr.shape[0] != len(labels) and arr.shape[1] == len(labels):
            arr = arr.T

        matrix = np.corrcoef(arr)
        correlation_matrix = pd.DataFrame(matrix, index=labels, columns=labels)
        self.add_log_entry(f"[RESULT] Correlation matrix computed for {len(labels)} variables.")
        return {"correlation_matrix": correlation_matrix}

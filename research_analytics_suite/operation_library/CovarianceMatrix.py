"""
Operation:      CovarianceMatrix
Version:        0.0.1
Description:    Compute the pairwise covariance matrix for a set of numeric columns.

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


class CovarianceMatrix(BaseOperation):
    """
    Compute the pairwise covariance matrix for a set of numeric columns.

    Requires:
        data (list): A list of equal-length numeric lists (each inner list is one variable).
        labels (list): Column labels for the variables (same order as data).

    Returns:
        covariance_matrix (list): 2-D list representing the covariance matrix.
        labels (list): The variable labels.
    """
    name = "CovarianceMatrix"
    version = "0.0.1"
    description = "Compute the pairwise covariance matrix."
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
        _inputs = self.get_inputs()
        data = _inputs.get("data", [])
        labels = _inputs.get("labels", [])

        matrix = np.cov(data).tolist()
        self.add_log_entry(f"[RESULT] Covariance matrix computed for {len(labels)} variables.")
        return {"covariance_matrix": matrix, "labels": labels}

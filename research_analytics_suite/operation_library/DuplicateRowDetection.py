"""
Operation:      DuplicateRowDetection
Version:        0.0.1
Description:    Detect and report duplicate rows in a dataset.

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


class DuplicateRowDetection(BaseOperation):
    """
    Detect and report duplicate rows in a dataset.

    Requires:
        data (list): List of dicts representing rows.
        subset (list): Optional list of column names to consider when identifying duplicates.
                       Pass an empty list to use all columns.

    Returns:
        duplicate_indices (list): Zero-based row indices of duplicate rows (all occurrences after first).
        n_duplicates (int): Number of duplicate rows.
        total_rows (int): Total number of rows.
        subset_used (list): Column names used for duplicate detection.
    """
    name = "DuplicateRowDetection"
    version = "0.0.1"
    description = "Detect and report duplicate rows in a dataset."
    category_id = 601
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"data": list, "subset": list}
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
        import pandas as pd

        _inputs = self.get_inputs()
        data = _inputs.get("data", [])
        subset = _inputs.get("subset", [])

        df = pd.DataFrame(data)
        total_rows = int(len(df))
        subset_used = subset if subset else list(df.columns)
        dup_mask = df.duplicated(subset=subset if subset else None, keep="first")
        duplicate_indices = [int(i) for i in df[dup_mask].index.tolist()]

        self.add_log_entry(
            f"[RESULT] {len(duplicate_indices)} duplicate rows out of {total_rows} total"
        )
        return {
            "duplicate_indices": duplicate_indices,
            "n_duplicates": len(duplicate_indices),
            "total_rows": total_rows,
            "subset_used": subset_used,
        }

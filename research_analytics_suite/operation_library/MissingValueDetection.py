"""
Operation:      MissingValueDetection
Version:        0.0.1
Description:    Report missing value counts and percentages per column in a dataset.

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


class MissingValueDetection(BaseOperation):
    """
    Report missing value counts and percentages per column in a dataset.

    Requires:
        data (list): List of dicts (rows) or list of lists (rows). If list of lists,
                     column_names should be provided.
        column_names (list): Optional column name labels when data is a list of lists.

    Returns:
        total_rows (int): Total number of rows.
        missing_per_column (dict): Mapping of column name to count of missing values.
        missing_pct_per_column (dict): Mapping of column name to percent missing (0-100).
        columns_with_missing (list): Names of columns that have at least one missing value.
    """
    name = "MissingValueDetection"
    version = "0.0.1"
    description = "Report missing value counts and percentages per column in a dataset."
    category_id = 601
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"data": list, "column_names": list}
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
        column_names = _inputs.get("column_names", [])

        if data and isinstance(data[0], list):
            df = pd.DataFrame(data, columns=column_names if column_names else None)
        else:
            df = pd.DataFrame(data)

        total_rows = int(len(df))
        missing_counts = df.isnull().sum()
        missing_per_column = {str(col): int(cnt) for col, cnt in missing_counts.items()}
        missing_pct_per_column = {
            str(col): float(round(cnt / total_rows * 100.0, 2)) if total_rows > 0 else 0.0
            for col, cnt in missing_counts.items()
        }
        columns_with_missing = [col for col, cnt in missing_per_column.items() if cnt > 0]

        self.add_log_entry(
            f"[RESULT] {total_rows} rows; {len(columns_with_missing)} columns with missing values"
        )
        return {
            "total_rows": total_rows,
            "missing_per_column": missing_per_column,
            "missing_pct_per_column": missing_pct_per_column,
            "columns_with_missing": columns_with_missing,
        }

"""
Operation:      ColumnTypeInference
Version:        0.0.1
Description:    Infer the likely correct data type for each column and flag type mismatches.

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


class ColumnTypeInference(BaseOperation):
    """
    Infer the likely correct data type for each column and flag type mismatches.
    For each column, attempts coercion to numeric, boolean, and datetime to determine
    the most appropriate type. Flags columns where stored type differs from inferred type.

    Requires:
        data (list): List of dicts representing rows.

    Returns:
        inferred_types (dict): Mapping of column name to inferred type string.
        stored_types (dict): Mapping of column name to pandas dtype string.
        mismatched_columns (list): Columns where inferred type differs from stored type.
    """
    name = "ColumnTypeInference"
    version = "0.0.1"
    description = "Infer the likely correct data type for each column and flag type mismatches."
    category_id = 601
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"data": list}
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

        df = pd.DataFrame(data)
        stored_types = {str(col): str(df[col].dtype) for col in df.columns}
        inferred_types = {}

        for col in df.columns:
            series = df[col].dropna()
            col_str = str(col)
            if len(series) == 0:
                inferred_types[col_str] = "unknown"
                continue

            numeric_result = pd.to_numeric(series, errors="coerce")
            if numeric_result.notna().all():
                if (numeric_result == numeric_result.astype(int)).all():
                    inferred_types[col_str] = "integer"
                else:
                    inferred_types[col_str] = "float"
                continue

            bool_vals = {"true", "false", "1", "0", "yes", "no"}
            if series.astype(str).str.lower().isin(bool_vals).all():
                inferred_types[col_str] = "boolean"
                continue

            dt_result = pd.to_datetime(series, errors="coerce", infer_datetime_format=True)
            if dt_result.notna().all():
                inferred_types[col_str] = "datetime"
                continue

            inferred_types[col_str] = "string"

        mismatched_columns = []
        for col in df.columns:
            col_str = str(col)
            inferred = inferred_types.get(col_str, "unknown")
            stored = stored_types.get(col_str, "")
            is_numeric_stored = "int" in stored or "float" in stored
            is_numeric_inferred = inferred in ("integer", "float")
            if is_numeric_stored and is_numeric_inferred:
                continue
            if inferred == "string" and stored == "object":
                continue
            if inferred != "unknown" and not (is_numeric_stored and is_numeric_inferred):
                type_map = {
                    "integer": "int64",
                    "float": "float64",
                    "boolean": "bool",
                    "datetime": "datetime64[ns]",
                    "string": "object",
                }
                if type_map.get(inferred, inferred) != stored:
                    mismatched_columns.append(col_str)

        self.add_log_entry(
            f"[RESULT] {len(mismatched_columns)} columns with type mismatches "
            f"out of {len(df.columns)} total"
        )
        return {
            "inferred_types": inferred_types,
            "stored_types": stored_types,
            "mismatched_columns": mismatched_columns,
        }

"""
Operation:      GroupByOperations
Version:        0.0.1
Description:    Perform group by operations on a dataset.

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
import pandas as pd
from typing import Optional, Type, List
from research_analytics_suite.operation_manager import BaseOperation


class GroupByOperations(BaseOperation):
    """
    Perform group by operations on a dataset.

    Requires:
        dataframe (pd.DataFrame): The pandas DataFrame to perform group by operations on.
        group_by_columns (List[str]): The columns to group by.
        agg_function (str): The aggregation function to apply (e.g., 'sum', 'mean').

    Returns:
        grouped_data (pd.DataFrame): The grouped DataFrame.
    """
    name = "GroupByOperations"
    version = "0.0.1"
    description = "Perform group by operations on a dataset."
    category_id = 1201
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"dataframe": pd.DataFrame, "group_by_columns": list, "agg_function": str}
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
        Execute the operation's logic: perform group by operations on the DataFrame.
        """
        _inputs = self.get_inputs()
        dataframe = _inputs.get("dataframe")
        group_by_columns = _inputs.get("group_by_columns", [])
        agg_function = _inputs.get("agg_function", "sum")

        grouped_data = dataframe.groupby(group_by_columns).agg(agg_function)
        self.add_log_entry(f"[RESULT] Group by operations executed successfully. Resulting DataFrame: {str(grouped_data.head())}")
        return {"grouped_data": grouped_data}
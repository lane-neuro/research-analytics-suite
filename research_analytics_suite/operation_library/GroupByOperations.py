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

    Attributes:
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
    unique_id = f"{github}_{name}_{version}"
    required_inputs = {"dataframe": pd.DataFrame, "group_by_columns": list, "agg_function": str}
    parent_operation: Optional[Type[BaseOperation]] = None
    inheritance: Optional[list] = []
    is_loop = False
    is_cpu_bound = False
    parallel = False

    def __init__(self, dataframe: pd.DataFrame, group_by_columns: List[str], agg_function: str, *args, **kwargs):
        """
        Initialize the operation with the DataFrame, group by columns, and aggregation function.

        Args:
            dataframe (pd.DataFrame): The pandas DataFrame to perform group by operations on.
            group_by_columns (List[str]): The columns to group by.
            agg_function (str): The aggregation function to apply (e.g., 'sum', 'mean').
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self.dataframe = dataframe
        self.group_by_columns = group_by_columns
        self.agg_function = agg_function
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
        grouped_data = self.dataframe.groupby(self.group_by_columns).agg(self.agg_function)
        print(f"Grouped Data:\n{grouped_data}")

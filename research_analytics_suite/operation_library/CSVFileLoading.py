"""
Operation:      CSVFileLoading
Version:        0.0.1
Description:    Load data from a CSV file.

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
from typing import Optional, Type
from research_analytics_suite.operation_manager import BaseOperation


class CSVFileLoading(BaseOperation):
    """
    Load data from a CSV file.

    Requires:
        file_path (str): The path to the CSV file to be loaded.

    Returns:
        data (dict): The data loaded from the CSV file.
    """
    name = "CSVFileLoading"
    version = "0.0.1"
    description = "Load data from a CSV file."
    category_id = 1101
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"file_path": str}
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
        Execute the operation's logic: load data from the CSV file and return it as a dictionary.
        """
        _inputs = self.get_inputs()
        _file_path = _inputs.get("file_path", "")

        data = pd.read_csv(_file_path)
        self.add_log_entry(f"[RESULT] Loaded data: {data}")
        return {"csv_data": data.to_dict()}

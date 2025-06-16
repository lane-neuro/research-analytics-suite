"""
Operation:      FieldObservation
Version:        0.0.1
Description:    Collect data through field observations.

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


class FieldObservation(BaseOperation):
    """
    Collect data through field observations.

    Requires:
        observations (List[dict]): The field observations to analyze.

    Returns:
        observations (List[dict]): The list of observations that were analyzed.
    """
    name = "FieldObservation"
    version = "0.0.1"
    description = "Collect data through field observations."
    category_id = 902
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"observations": list}
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
        Execute the operation's logic: analyze the field observations.
        """
        _inputs = self.get_inputs()
        _observations = _inputs.get("observations", [])

        # Placeholder for field observation analysis logic
        self.add_log_entry(f"Adding {len(_observations)} observations to workspace database.")
        return {"observations": _observations}

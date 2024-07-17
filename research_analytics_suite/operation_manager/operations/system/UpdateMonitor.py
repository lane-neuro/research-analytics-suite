"""
UpdateMonitor Module

The UpdateMonitor class is designed to execute an update function.

Author: Lane
Copyright: Lane
Credits: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
from research_analytics_suite.operation_manager.operations.core.BaseOperation import BaseOperation


class UpdateMonitor(BaseOperation):
    """
    The `UpdateMonitor` System Operation is designed to execute an update function.
    """
    version = "0.0.1"
    description = "Executes an update function."
    category_id = -1
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {}
    parent_operation = None
    inheritance = []
    is_loop = True
    is_cpu_bound = False
    parallel = True

    def __init__(self, *args, **kwargs):
        """
        Initializes the `UpdateMonitor` System Operation with the specified update function.

        Args:
            update_function: The async function to be executed.
        """
        super().__init__(*args, **kwargs)

    async def initialize_operation(self) -> None:
        """Initializes the operation."""
        await super().initialize_operation()
        self.is_ready = True

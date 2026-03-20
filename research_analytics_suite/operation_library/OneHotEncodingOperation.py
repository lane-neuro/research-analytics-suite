"""
Operation:      OneHotEncodingOperation
Version:        0.0.1
Description:    One-hot encode a categorical column into binary indicator columns.

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


class OneHotEncodingOperation(BaseOperation):
    """
    One-hot encode a categorical column.

    Requires:
        categories (list): A list of categorical string (or int) values to encode.

    Returns:
        encoded (list): List of dicts, each dict maps category label to 0 or 1.
        classes (list): Sorted list of unique category labels found.
    """
    name = "OneHotEncodingOperation"
    version = "0.0.1"
    description = "One-hot encode a categorical column into binary indicator columns."
    category_id = 602
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"categories": list}
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
        _inputs = self.get_inputs()
        categories = _inputs.get("categories", [])

        classes = sorted(set(str(c) for c in categories))
        encoded = [{cls: (1 if str(val) == cls else 0) for cls in classes}
                   for val in categories]

        self.add_log_entry(
            f"[RESULT] One-hot encoded {len(categories)} row(s) into {len(classes)} class column(s)."
        )
        return {"encoded": encoded, "classes": classes}

"""
Operation:      WordCount
Version:        0.0.1
Description:    Count the number of words in a text.

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


class WordCount(BaseOperation):
    """
    Count the number of words in a text.

    Requires:
        text (str): The text to count the words.

    Returns:
        word_count (int): The number of words in the text.
    """
    name = "WordCount"
    version = "0.0.1"
    description = "Count the number of words in a text."
    category_id = 301
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"text": str}
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
        self.text = text
        super().__init__(*args, **kwargs)

    async def initialize_operation(self):
        """
        Initialize any resources or setup required for the operation before it starts.
        """
        await super().initialize_operation()

    async def execute(self):
        """
        Execute the operation's logic: count the number of words in the text.
        """
        _inputs = self.get_inputs()
        _text = _inputs.get("text", "")

        word_count = len(_text.split())
        self.add_log_entry(f"[RESULT] Word Count: {word_count}")
        return {"word_count": word_count}

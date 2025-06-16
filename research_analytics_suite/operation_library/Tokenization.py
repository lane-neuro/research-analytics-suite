"""
Operation:      Tokenization
Version:        0.0.1
Description:    Tokenize a text into words or sentences.

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


class Tokenization(BaseOperation):
    """
    Tokenize a text into words or sentences.

    Requires:
        text (str): The text to tokenize.

    Returns:
        tokens (List[str]): The list of tokens.
    """
    name = "Tokenization"
    version = "0.0.1"
    description = "Tokenize a text into words or sentences."
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
        super().__init__(*args, **kwargs)

    async def initialize_operation(self):
        """
        Initialize any resources or setup required for the operation before it starts.
        """
        await super().initialize_operation()

    async def execute(self):
        """
        Execute the operation's logic: tokenize the text into words.
        """
        _inputs = self.get_inputs()
        text = _inputs.get("text", "")

        tokens = text.split()
        self.add_log_entry(f"[RESULT] Tokens: {str(tokens)}")
        return {"tokens": tokens}


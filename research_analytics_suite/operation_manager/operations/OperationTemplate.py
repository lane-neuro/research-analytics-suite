"""
Operation:      [Operation Name]
Version:        [0.0.1]
Description:    [A template class to help developers create their own Operation classes by extending BaseOperation.
                This template provides a starting point for creating new operations with the necessary attributes
                and methods. Developers can customize the operation by adding their own logic and attributes
                as needed. Replace any '[placeholders]' with the actual values for the operation.]

Author:         [Your Name]
GitHub:         [Your GitHub Username] (optional)
Email:          [Your Email Address] (optional)

---
Part of the Research Analytics Suite
    https://github.com/lane-neuro/research-analytics-suite
License:        BSD 3-Clause License
Maintainer:     Lane (GitHub: @lane-neuro)
Status:         Template
"""
from typing import Optional, Type
from research_analytics_suite.operation_manager import BaseOperation


class OperationTemplate(BaseOperation):
    """
    [OperationTemplate class extends the BaseOperation class to provide a basic template for creating new operations.
        To create a new operation, follow these steps:
        1. Define the operation-specific attributes and methods.
        2. Override the `execute` method to implement the operation's logic.
        3. Add any additional methods required for the operation.]

    Refer to ExampleOperation.py for an example of a concrete implementation of an operation.

    Methods:
        [custom_method]: [Example of a custom method.]

    Returns:
        [variable_name] ([type]) - [Description of the variable returned by the operation.]
    """

    # Preset attributes to be defined by the operation creator
    name: str = "DefaultOperationName"
    version: str = "0.0.1"
    description: str = "Default operation description."
    category_id: int = 0
    author: str = "Default Author"
    github: str = "[no-github]"
    email: str = "[no-email]"
    required_inputs: dict[str, type] = {"text_in": str} # Example of a required input
    parent_operation: Optional[Type[BaseOperation]] = None
    inheritance: list = []
    is_loop: bool = False
    is_cpu_bound: bool = True
    is_gpu_bound: bool = False
    parallel: bool = False

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize the operation instance. Update kwargs with preset attributes and call the parent class constructor.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        # Call the parent class constructor
        super().__init__(*args, **kwargs)

    async def initialize_operation(self) -> None:
        """
        Initialize any resources or setup required for the operation before it starts.
        """
        await super().initialize_operation()

    async def execute(self):
        """
        Execute the operation's logic.
        """
        # Get the inputs for the operation and assign them to local variables
        inputs = self.get_inputs()
        _text_in = inputs["text_in"]

        # Example: Print the input value
        print(f"text_in: {_text_in}")

        # Example: Count the number of characters in the input string
        _num_chars = len(_text_in)

        # Example: Run post-execution logic
        await self.post_execute()

        # Return the number of characters as the output
        return {"num_chars": _num_chars}

    async def post_execute(self) -> None:
        """
        Logic to run after the main execution.
            This optional method is an example; not required by BaseOperation.
        """
        self._progress = 100
        self._status = "completed"
        self.add_log_entry("OperationTemplate completed.")

    def validate(self) -> None:
        """
        Validate inputs and outputs of the operation.
            This optional method is an example; not required by BaseOperation.
        """
        pass

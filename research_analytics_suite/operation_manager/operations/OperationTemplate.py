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

    Attributes:
        custom_attribute: [Example of a custom attribute.]

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
    required_inputs: dict[str, type] = {}
    # output_parameters: Optional[dict[str, type]] = {}
    parent_operation: Optional[Type[BaseOperation]] = None
    inheritance: list = []
    is_loop: bool = False
    is_cpu_bound: bool = False
    parallel: bool = False

    def __init__(self, custom_attribute: Optional[any], *args, **kwargs) -> None:
        """
        Initialize the operation instance. Update kwargs with preset attributes and call the parent class constructor.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self.action = self.execute   # Default action is execute()

        # Update kwargs with preset attributes
        kwargs.update({
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'category_id': self.category_id,
            'author': self.author,
            'github': self.github,
            'email': self.email,
            'action': self.action,
            'required_inputs': self.required_inputs,        # dict[str, type] of required input parameters
            # 'output_parameters': self.output_parameters,   # dict[str, type] of output parameters
            'parent_operation': self.parent_operation,
            'inheritance': self.inheritance,                # list of unique IDs of child operations
            'is_loop': self.is_loop,
            'is_cpu_bound': self.is_cpu_bound,
            'parallel': self.parallel
        })

        # Call the parent class constructor
        super().__init__(*args, **kwargs)

        # Custom attributes
        self._custom_attribute = custom_attribute

    async def initialize_operation(self) -> None:
        """
        Initialize any resources or setup required for the operation before it starts.
        """
        await super().initialize_operation()

    async def pre_execute(self) -> None:
        """
        Logic to run before the main execution.
            This optional method is an example; not required by BaseOperation.
        """
        pass

    async def execute(self) -> None:
        """
        Execute the operation's logic.
        """
        await self.pre_execute()

        # Example: Print the template attribute
        print(f"custom_attribute: {self._custom_attribute}")

        await self.post_execute()

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

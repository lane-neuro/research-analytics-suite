"""
Operation: [Operation Name]
Version: [0.0.1]
Description: [A template class to help developers create their own Operation classes by extending BaseOperation.
             This template provides a starting point for creating new operations with the necessary attributes
             and methods. Developers can customize the operation by adding their own logic and attributes
             as needed. Replace any '[placeholders]' with the actual values for the operation.]

Author: [Your Name]
GitHub: [Your GitHub Username] (optional)
Email: [Your Email Address] (optional)

---
Part of the Research Analytics Suite
    https://github.com/lane-neuro/research-analytics-suite
License: BSD 3-Clause License
Maintainer: Lane
Status: Template
"""
from typing import Any, Dict, Optional, Type

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
        name (str): The name of the operation.
        version (str): The version of the operation.
        description (str): The description of the operation.
        category_id (int): The category ID of the operation.
        author (str): The author of the operation.
        github (str): The GitHub username of the author.
        email (str): The email address of the author.
        unique_id (str): The unique ID of the operation.
        action: The action to be executed by the operation.
        required_inputs (Optional[dict[str, type]): Required inputs for the operation.
        parent_operation (Optional[Type[BaseOperation]]): Parent operation.
        inheritance (Optional[Dict[str, Type[BaseOperation]]]): Required child operations.
        is_loop (bool): Whether the operation should run in a loop.
        is_cpu_bound (bool): Whether the operation is CPU-bound.
        parallel (bool): Whether inherited/child operations should run in parallel or sequentially.
        custom_attribute: [Example of a custom attribute.]

    Methods:
        __init__: Initialize the operation.
        initialize_operation: Initialize any resources or setup required for the operation.
        execute: Execute the operation's logic.
        pre_execute: Logic to run before the main execution.
        post_execute: Logic to run after the main execution.
        validate: Validate inputs and outputs of the operation.
        [custom_method]: [Example of a custom method.]
    """

    # Preset attributes to be defined by the operation creator
    name: str = "DefaultOperationName"
    version: str = "0.0.1"
    description: str = "Default operation description."
    category_id: int = 0
    author: str = "Default Author"
    github: str = "lane-neuro"
    email: str = "default_author@email.com"
    unique_id: str = f"{github}_{name}_{version}"
    # action is set to execute() within the __init__ method by default
    required_inputs: Optional[dict[str, type]] = None
    parent_operation: Optional[Type[BaseOperation]] = None
    inheritance: Optional[Dict[str, Type[BaseOperation]]] = None
    is_loop: bool = False
    is_cpu_bound: bool = False
    parallel: bool = False

    def __init__(self, custom_attribute: Optional[Any], *args: Any, **kwargs: Any):
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
            'unique_id': self.unique_id,
            'action': self.action,
            'required_inputs': self.required_inputs,
            'parent_operation': self.parent_operation,
            'inheritance': self.inheritance,
            'is_loop': self.is_loop,
            'is_cpu_bound': self.is_cpu_bound,
            'parallel': self.parallel
        })

        # Call the parent class constructor
        super().__init__(*args, **kwargs)

        # Custom attributes
        self._custom_attribute = custom_attribute

    async def initialize_operation(self):
        """
        Initialize any resources or setup required for the operation before it starts.
        """
        await super().initialize_operation()

    async def pre_execute(self):
        """
        Logic to run before the main execution.
            This optional method is an example; not required by BaseOperation.
        """
        pass

    async def execute(self):
        """
        Execute the operation's logic.
        """
        await self.pre_execute()

        # Example: Print the template attribute
        print(f"custom_attribute: {self._custom_attribute}")

        await self.post_execute()

    async def post_execute(self):
        """
        Logic to run after the main execution.
            This optional method is an example; not required by BaseOperation.
        """
        self._progress = 100
        self._status = "completed"
        self.add_log_entry("OperationTemplate completed.")

    def validate(self):
        """
        Validate inputs and outputs of the operation.
            This optional method is an example; not required by BaseOperation.
        """
        pass

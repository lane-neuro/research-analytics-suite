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
        persistent (bool): Whether the operation should run indefinitely.
        is_cpu_bound (bool): Whether the operation is CPU-bound.
        concurrent (bool): Whether child operations should run concurrently.
        required_parent (Optional[Type[BaseOperation]]): Required parent operation type.
        required_children (Optional[Dict[str, Type[BaseOperation]]]): Required child operations.
        required_dependencies (Optional[Dict[str, Type[BaseOperation]]]): Required dependencies.
    Custom Attributes:
        [custom_attribute]: [Example of a custom attribute.]

    Methods:
        __init__: Initialize the operation.
        initialize_operation: Initialize any resources or setup required for the operation.
        execute: Execute the operation's logic.
        pre_execute: Logic to run before the main execution.
        post_execute: Logic to run after the main execution.
        validate: Validate inputs and outputs of the operation.
    Custom Methods:
        [custom_method]: [Example of a custom method.]
    """

    # Preset attributes to be defined by the operation creator
    name: str = "DefaultOperationName"
    persistent: bool = False
    is_cpu_bound: bool = False
    concurrent: bool = False
    required_parent: Optional[Type[BaseOperation]] = None
    required_children: Optional[Dict[str, Type[BaseOperation]]] = None
    required_dependencies: Optional[Dict[str, Type[BaseOperation]]] = None

    def __init__(self, template_attribute: Optional[Any], *args: Any, **kwargs: Any):
        """
        Initialize the operation instance. Update kwargs with preset attributes and call the parent class constructor.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        # Update kwargs with preset attributes
        kwargs.update({
            'name': self.name,
            'action': self.execute,
            'persistent': self.persistent,
            'is_cpu_bound': self.is_cpu_bound,
            'concurrent': self.concurrent
        })
        self._required_parent = self.required_parent
        self._required_children = self.required_children
        self._required_dependencies = self.required_dependencies

        # Call the parent class constructor
        super().__init__(*args, **kwargs)

        # Custom attributes
        self._template_attribute = template_attribute

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
        print(f"Template attribute: {self._template_attribute}")

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

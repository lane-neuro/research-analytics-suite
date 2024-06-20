"""
A module that defines the DaskOperation class, a subclass of the Operation class.

The DaskOperation class is designed to handle Dask computations. It provides methods for setting the Dask computation
to be processed and executing the operations.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

import dask
import dask.distributed

from research_analytics_suite.operation_manager.operations.core.BaseOperation import BaseOperation


class DaskOperation(BaseOperation):
    """
    A class used to represent a Dask Operation in the Research Analytics Suite.

    This class provides methods for setting the Dask computation to be processed and executing the operations.

    Attributes:
        _action (callable): A Dask computation function to be executed.
        local_vars (dict): Local variables to be used in the function execution.
        client (dask.distributed.Client): The Dask client for managing the computation.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the Dask operation instance.

        Args:
            action (callable, optional): The Dask computation to be executed by the operation.
            name (str, optional): The name of the operation. Defaults to "DaskOperation".
            persistent (bool, optional): Whether the operation should run indefinitely. Defaults to False.
            is_cpu_bound (bool, optional): Whether the operation is CPU-bound. Defaults to False.
            concurrent (bool, optional): Whether child operations should run concurrently. Defaults to False.
            parent_operation (BaseOperation, optional): The parent operation. Defaults to None.
            local_vars (dict, optional): Local variables for the function execution. Defaults to None.
            client (dask.distributed.Client, optional): The Dask client for managing the computation.
        """
        self._client = kwargs.pop('client', None)
        super().__init__(*args, **kwargs)

    @property
    def client(self):
        """Gets the Dask client for managing the computation."""
        return self._client

    @client.setter
    def client(self, value):
        """Sets the Dask client for managing the computation."""
        if not isinstance(value, dask.distributed.Client):
            raise ValueError("client must be an instance of dask.distributed.Client")
        self._client = value

    async def initialize_operation(self):
        """
        Initialize any resources or setup required for the Dask operation before it starts.
        """
        await super().initialize_operation()
        if self._client is None:
            self._client = dask.distributed.Client()

    async def execute_action(self):
        """
        Execute the Dask computation associated with the operation.

        Returns:
            The result of the Dask computation.
        """
        temp_vars = self._local_vars.copy()
        try:
            # Execute the Dask computation
            future = self.client.submit(self._action)
            self._result_output = future.result()
        except Exception as e:
            self.status = "error"
            self._handle_error(e)
        finally:
            self._local_vars = temp_vars

    def get_result(self):
        """
        Retrieve the result of the Dask computation.

        Returns:
            The result of the Dask computation.
        """
        return self._result_output

    def cleanup_operation(self):
        """
        Clean up any resources or perform any necessary teardown after the Dask operation has completed or been stopped.
        """
        if self.client:
            self.client.close()
        super().cleanup_operation()

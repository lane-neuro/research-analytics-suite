"""
This module provides the DataTransformer class which is used to transform data using Dask.

The DataTransformer class inherits from the Operation class and overrides its methods to provide
data transformation functionality. It uses Dask to perform the transformations in a parallel and
efficient manner.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

from dask import delayed
import dask.bag as db
from dask.distributed import Client
from neurobehavioral_analytics_suite.operation_handler.operations.Operation import Operation


class DataTransformer(Operation):
    """A class used to transform data using Dask.

    Attributes:
        transformed_data: The transformed data.
        error_handler: The error handler.
        data: The original data.
        transform_func: The function to apply the transformation.
        client: The Dask distributed client.
    """

    def __init__(self, error_handler, data, transform_func):
        """Initializes the DataTransformer with the given error handler, data, and transformation function."""
        super().__init__(name="DataTransformerOperation")
        self.transformed_data = None
        self.error_handler = error_handler
        self.data = data
        self.transform_func = transform_func  # The function to apply the transformation
        self.client = Client()  # Initialize Dask distributed client

    async def execute(self):
        """Executes the transformation function on the data and returns the transformed data."""
        # Check the type of transform_func and apply it accordingly
        if self.transform_func.__name__ in ['map', 'filter', 'random_sample']:
            self.transformed_data = self.data.map(self.transform_func)
        elif self.transform_func.__name__ in ['reduce', 'fold', 'groupby', 'frequencies', 'topk']:
            self.transformed_data = getattr(self.data, self.transform_func.__name__)(self.transform_func)
        else:
            raise ValueError(f"Unsupported transformation function: {self.transform_func.__name__}")
        return self.client.compute(self.transformed_data)  # Compute using Dask distributed client

    def transform(self, data):
        """Transforms the data. This method should be overridden by subclasses."""
        pass

    async def start(self):
        """Starts the data transformation."""
        self.status = "started"

    async def stop(self):
        """Stops the data transformation."""
        self.status = "stopped"

    async def pause(self):
        """Pauses the data transformation."""
        self.status = "paused"
        self.pause_event.clear()

    async def resume(self):
        """Resumes the data transformation."""
        self.status = "running"
        self.pause_event.set()

    async def reset(self):
        """Resets the data transformation."""
        self.status = "idle"
        self.progress = 0
        self.complete = False
        self.pause_event.clear()
        await self.stop()
        await self.start()

    def progress(self):
        """Returns the progress and status of the data transformation."""
        return self.progress, self.status

    def validate_data(self, data):
        """Validates the data. Raises a ValueError if the data is not a Dask Bag."""
        # Check if the data is a Dask Bag
        if not isinstance(data, db.Bag):
            raise ValueError("Invalid data: Expected a Dask Bag")

    def log(self, message):
        """Logs the given message."""
        print(message)

    def handle_error(self, exception):
        """Handles the given exception by logging it and re-raising it."""
        # Log the error and re-raise the exception
        self.log(f"An error occurred: {str(exception)}")
        raise exception

    def get_transformed_data(self):
        """Returns the transformed data."""
        return self.transformed_data

    def set_transform_func(self, transform_func):
        """Sets a new transformation function."""
        self.transform_func = transform_func

    def get_transform_func(self):
        """Returns the current transformation function."""
        return self.transform_func

    def get_data(self):
        """Returns the original data."""
        return self.data

    def set_data(self, data):
        """Sets new data."""
        self.data = data

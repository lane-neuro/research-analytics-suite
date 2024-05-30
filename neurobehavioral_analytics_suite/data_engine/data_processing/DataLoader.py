"""
This module provides the DataLoader class which is used to load transformed data using Dask.

The DataLoader class inherits from the Operation class and overrides its methods to provide
data loading functionality. It uses Dask to perform the loading in a parallel and efficient manner.

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
from dask.distributed import Client
import dask.bag as db
from neurobehavioral_analytics_suite.operation_manager.operation.Operation import Operation


class DataLoader(Operation):
    """A class used to load transformed data using Dask.

    Attributes:
        loaded_data: The loaded data.
        error_handler: The error handler.
        transformed_data: The transformed data.
        data_destination: The destination to load the data.
        client: The Dask distributed client.
    """

    def __init__(self, error_handler, transformed_data, data_destination):
        """Initializes the DataLoader with the given error handler, transformed data, and data destination."""
        super().__init__(name="DataLoaderOperation")
        self.loaded_data = None
        self.error_handler = error_handler
        self.transformed_data = transformed_data
        self.data_destination = data_destination
        self.client = Client()  # Initialize Dask distributed client

    async def execute(self):
        """Executes the loading of the transformed data and returns the loaded data."""
        self.loaded_data = delayed(self.load)(self.transformed_data, self.data_destination)
        return self.client.compute(self.loaded_data)  # Compute using Dask distributed client

    def load(self, transformed_data, data_destination):
        """Loads the transformed data to the given data destination."""
        if isinstance(transformed_data, db.Bag):
            transformed_data.to_textfiles(data_destination + '/*.txt')
        else:
            raise ValueError("Unsupported data type for DataLoader")

    async def start(self):
        """Starts the data loading."""
        self.status = "started"

    async def stop(self):
        """Stops the data loading."""
        self.status = "stopped"

    async def pause(self):
        """Pauses the data loading."""
        self.status = "paused"
        self.pause_event.clear()

    async def resume(self):
        """Resumes the data loading."""
        self.status = "running"
        self.pause_event.set()

    async def reset(self):
        """Resets the data loading."""
        self.status = "idle"
        self.progress = 0
        self.complete = False
        self.pause_event.clear()
        await self.stop()
        await self.start()

    def progress(self):
        """Returns the progress and status of the data loading."""
        return self.progress, self.status

    def validate_data(self, transformed_data):
        """Validates the transformed data. Raises a ValueError if the transformed data is not a Dask Bag."""
        # Check if the transformed_data is a Dask Bag
        if not isinstance(transformed_data, db.Bag):
            raise ValueError("Invalid data: Expected a Dask Bag")

    def log(self, message):
        """Logs the given message."""
        print(message)

    def handle_error(self, exception):
        """Handles the given exception by logging it and re-raising it."""
        # Log the error and re-raise the exception
        self.log(f"An error occurred: {str(exception)}")
        raise exception

    def is_complete(self):
        """Checks if the data loading is complete."""
        # Check if the loaded_data is not None and the status is "completed"
        return self.loaded_data is not None and self.status == "completed"

    def get_loaded_data(self):
        """Returns the loaded data."""
        return self.loaded_data

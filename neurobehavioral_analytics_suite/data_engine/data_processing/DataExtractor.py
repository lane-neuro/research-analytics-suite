"""
This module provides the DataExtractor class which is used to extract data from various sources using Dask.

The DataExtractor class inherits from the Operation class and overrides its methods to provide
data extraction functionality. It uses Dask to perform the extraction in a parallel and efficient manner.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

import json
import urllib.parse
import dask.bag as db
import requests
from dask import delayed
from dask.distributed import Client
from neurobehavioral_analytics_suite.operation_manager.operations.Operation import Operation


class DataExtractor(Operation):
    """A class used to extract data from various sources using Dask.

    Attributes:
        data: The extracted data.
        error_handler: The error handler.
        data_source: The source of the data.
        data_format: The format of the data.
        client: The Dask distributed client.
    """

    def __init__(self, error_handler, data_source, data_format=None):
        """Initializes the DataExtractor with the given error handler, data source, and data format."""
        super().__init__(name="DataExtractorOperation", error_handler=error_handler, func=self.execute)
        self.data = None
        self.data_source = data_source
        self.data_format = data_format
        self.client = Client()  # Initialize Dask distributed client

    async def execute(self):
        """Executes the extraction of the data and returns the extracted data."""
        if self.is_url(self.data_source):
            self.data = delayed(self.extract_from_url)(self.data_source, self.data_format)
        else:
            print("Extracting data...")
            self.data = delayed(self.extract)(self.data_source, self.data_format)
        return self.client.compute(self.data)  # Compute using Dask distributed client

    async def extract(self, data_source, data_format):
        """Extracts the data from the given data source in the given data format."""
        if data_format == 'json':
            data = db.read_text(data_source).map(json.loads)
        elif data_format == 'csv':
            data = db.read_text(data_source).str.split(',').to_dataframe()
        else:
            raise ValueError(f"Unsupported data format: {data_format}")
        return data

    async def extract_from_url(self, url, data_format):
        """Extracts the data from the given URL in the given data format."""
        response = requests.get(url)
        if data_format == 'json':
            data = json.loads(response.text)
        elif data_format == 'csv':
            data = [row.split(',') for row in response.text.split('\n')]
        else:
            raise ValueError(f"Unsupported data format: {data_format}")
        return data

    async def start(self):
        """Starts the data extraction."""
        self.status = "started"

    async def stop(self):
        """Stops the data extraction."""
        self.status = "stopped"

    async def pause(self):
        """Pauses the data extraction."""
        self.status = "paused"
        self._pause_event.clear()

    async def resume(self):
        """Resumes the data extraction."""
        self.status = "running"
        self._pause_event.set()

    async def reset(self):
        """Resets the data extraction."""
        self.status = "idle"
        self.progress = 0
        self._complete = False
        self._pause_event.clear()
        await self.stop()
        await self.start()

    def is_url(self, data_source):
        """Checks if the given data source is a URL."""
        try:
            result = urllib.parse.urlparse(data_source)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

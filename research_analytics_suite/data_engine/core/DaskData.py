"""
DaskData Module

Defines the DaskData class for handling data using Dask in the Research Analytics Suite.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

import dask.dataframe as dd
import pandas as pd

from research_analytics_suite.data_engine.core.BaseData import BaseData


class DaskData(BaseData):
    """
    A class to handle data using Dask.

    Attributes:
        data: The data point.
        dask_dataframe: Dask DataFrame created from the data point.
    """
    def __init__(self, data):
        """
        Initializes the DaskData instance.

        Args:
            data: The data point.
        """
        super().__init__(data)
        self.dask_dataframe = self.set_dataframe(data)

    def apply(self, action):
        """
        Applies a function to the Dask DataFrame.

        Args:
            action (function): The function to apply to the Dask DataFrame.
        """
        if self.dask_dataframe is not None:
            self.dask_dataframe = self.dask_dataframe.map_partitions(action)
        return self

    def set_dataframe(self, data) -> dd.DataFrame:
        """
        Sets the Dask DataFrame.

        Args:
            data: The data point.
        """
        if isinstance(data, dd.DataFrame):
            self.dask_dataframe = data
        elif isinstance(data, pd.DataFrame):
            self.dask_dataframe = dd.from_pandas(data, npartitions=4)
        return self.dask_dataframe

    def compute(self):
        """
        Computes the Dask DataFrame.

        Returns:
            The computed Dask DataFrame.
        """
        return self.dask_dataframe.compute()

"""
UnifiedDataEngine Module

Defines the UnifiedDataEngine class that combines functionalities from DaskData and TorchData
to provide a unified interface for handling data.

Author: Lane
"""
import json
import uuid
from torch.utils.data import DataLoader
import dask.dataframe as dd
import pandas as pd
from research_analytics_suite.analytics.AnalyticsCore import AnalyticsCore
from research_analytics_suite.data_engine.DaskData import DaskData
from research_analytics_suite.data_engine.DataCache import DataCache
from research_analytics_suite.data_engine.TorchData import TorchData
from research_analytics_suite.data_engine.live_input.BaseInput import BaseInput
from research_analytics_suite.data_engine.DataTypeDetector import DataTypeDetector
from research_analytics_suite.utils.CustomLogger import CustomLogger
import joblib
import os


class UnifiedDataEngine:
    """
    A class that combines functionalities from DaskData and TorchData.

    Attributes:
        data: The data point.
        backend: The backend to use ('dask' or 'torch').
        dask_client: Dask client instance.
        analytics: AnalyticsCore instance for analytics operations.
        dask_data: DaskData instance for handling data with Dask.
        torch_data: TorchData instance for handling data with PyTorch.
        data_cache: DataCache instance for caching data.
        live_input_source: Live data input source instance.
    """
    def __init__(self, backend='dask', dask_client=None, data=None, data_name=None):
        """
        Initializes the UnifiedDataEngine instance.

        Args:
            backend (str): The backend to use ('dask' or 'torch'). Default is 'dask'.
            dask_client: Dask client instance. Default is None.
            data: The data point. Default is None.
        """
        self.data = data
        self.data_name = f"{data_name}_{uuid.uuid4()}" if data_name else f"data_{uuid.uuid4()}"
        self.backend = backend
        self._logger = CustomLogger()
        self.dask_client = dask_client  # Pointer to primary Dask client
        self.analytics = AnalyticsCore()  # Initialize AnalyticsCore Engine
        self.dask_data = DaskData(data)
        self.torch_data = TorchData(data)
        self.data_cache = DataCache()  # Initialize DataCache
        self.live_input_source = None  # Initialize live input source
        self.engine_id = f"{uuid.uuid4()}"

    def load_data(self, file_path):
        """
        Loads data from the specified file path.

        Args:
            file_path (str): The path to the data file.
        """
        data_type = DataTypeDetector.detect_type(file_path)
        self._logger.info(f"Loading data from {file_path} as {data_type}")

        if data_type == 'csv':
            self.data = dd.read_csv(file_path)
        elif data_type == 'json':
            self.data = dd.read_json(file_path)
        elif data_type == 'parquet':
            self.data = dd.read_parquet(file_path)
        elif data_type == 'hdf5':
            self.data = dd.read_hdf(file_path)
        elif data_type == 'excel':
            pandas_df = pd.read_excel(file_path)
            self.data = dd.from_pandas(pandas_df, npartitions=1)
        else:
            raise ValueError(f"Unsupported data type: {data_type}")

        self._logger.info("Data loaded")

    def save_data(self, file_path):
        """
        Saves data to the specified file path.

        Args:
            file_path (str): The path to the data file.
        """
        data_type = DataTypeDetector.detect_type(file_path)
        self._logger.info(f"Saving data to {file_path} as {data_type}")

        if data_type == 'csv':
            self.data.to_csv(file_path, single_file=True)
        elif data_type == 'json':
            self.data.to_json(file_path)
        elif data_type == 'parquet':
            self.data.to_parquet(file_path)
        elif data_type == 'hdf5':
            self.data.to_hdf(file_path, key='data')
        elif data_type == 'excel':
            pandas_df = self.data.compute() if isinstance(self.data, dd.DataFrame) else self.data
            pandas_df.to_excel(file_path)
        else:
            raise ValueError(f"Unsupported data type: {data_type}")

        self._logger.info("Data saved")

    def save_engine(self, instance_path):
        engine_path = os.path.join(instance_path, 'engines', self.engine_id)
        os.makedirs(engine_path, exist_ok=True)
        data_path = os.path.join(instance_path, 'data')
        os.makedirs(data_path, exist_ok=True)
        data_path = os.path.join(data_path, f"{self.data_name}.joblib")

        with open(data_path, 'wb') as data_file:
            joblib.dump(self.data, data_file)

        metadata = {
            'data_name': self.data_name,
            'backend': self.backend,
            'engine_id': self.engine_id
        }
        with open(os.path.join(engine_path, 'metadata.json'), 'w') as metadata_file:
            json.dump(metadata, metadata_file)

        # Save a pickleable state of the engine
        engine_state = self.__getstate__()
        with open(os.path.join(engine_path, 'engine_state.joblib'), 'wb') as state_file:
            joblib.dump(engine_state, state_file)

        self._logger.info(f"Instance saved to {instance_path}")

    @staticmethod
    def load_engine(instance_path, engine_id):
        engine_path = os.path.join(instance_path, 'engines', engine_id)
        with open(os.path.join(engine_path, 'metadata.json'), 'r') as metadata_file:
            metadata = json.load(metadata_file)

        data_path = os.path.join(instance_path, 'data', f"{metadata['data_name']}.joblib")
        with open(data_path, 'rb') as data_file:
            data = joblib.load(data_file)

        with open(os.path.join(engine_path, 'engine_state.joblib'), 'rb') as state_file:
            engine_state = joblib.load(state_file)

        engine = UnifiedDataEngine()
        engine.__setstate__(engine_state)
        engine.data = data
        return engine

    def set_backend(self, backend):
        """
        Sets the backend for the data engine.

        Args:
            backend (str): The backend to set ('dask' or 'torch').
        """
        if backend not in ['dask', 'torch']:
            raise ValueError("Backend must be either 'dask' or 'torch'")
        self.backend = backend

    def apply(self, func):
        """
        Applies a function to the data.

        Args:
            func (function): The function to apply to the data.
        """
        if self.backend == 'dask':
            self.dask_data.apply(func)
        elif self.backend == 'torch':
            self.torch_data = TorchData(func(self.torch_data.get_data()))

    def compute(self):
        """
        Computes the result for the data.

        Returns:
            The computed result.
        """
        if self.backend == 'dask':
            return self.dask_data.compute()
        elif self.backend == 'torch':
            return self.torch_data.get_data()

    def get_torch_loader(self, batch_size=32, shuffle=True):
        """
        Gets a PyTorch DataLoader for the data.

        Args:
            batch_size (int): The batch size for the DataLoader. Default is 32.
            shuffle (bool): Whether to shuffle the data. Default is True.

        Returns:
            DataLoader: The PyTorch DataLoader for the data.
        """
        if self.backend == 'torch':
            return DataLoader(self.torch_data, batch_size=batch_size, shuffle=shuffle)
        else:
            raise RuntimeError("DataLoader is only available for 'torch' backend")

    def get_pickleable_data(self):
        data = self.__dict__.copy()
        data.pop('logger', None)
        data.pop('dask_client', None)
        data.pop('live_input_source', None)
        return data

    def __getstate__(self):
        state = self.__dict__.copy()
        print(state)
        state['logger'] = None
        state['dask_client'] = None
        state['live_input_source'] = None
        state['cache'] = None
        state['analytics'] = None
        state['torch_data'] = None
        state['dask_data'] = None
        state['workspace'] = None
        state['live_data_handler'] = None
        print(state)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._logger = None
        self.dask_client = None
        self.live_input_source = None

    def cache_data(self, key, data):
        """
        Caches the given data with the specified key.

        Args:
            key (str): The key to associate with the cached data.
            data: The data to cache.
        """
        self.data_cache.set(key, data)

    def get_cached_data(self, key):
        """
        Retrieves cached data by key.

        Args:
            key (str): The key associated with the cached data.

        Returns:
            The cached data or None if the key is not found.
        """
        return self.data_cache.get(key)

    def clear_cache(self):
        """
        Clears all cached data.
        """
        self.data_cache.clear()

    def set_live_input(self, live_input: BaseInput):
        """
        Sets the live input source.

        Args:
            live_input (BaseInput): The live input source to set.
        """
        self.live_input_source = live_input

    def read_live_data(self):
        """
        Reads data from the live input source.

        Returns:
            The data read from the live input source.
        """
        if self.live_input_source:
            return self.live_input_source.read_data()
        return None

    def close_live_input(self):
        """
        Closes the live input source.
        """
        if self.live_input_source:
            self.live_input_source.close()

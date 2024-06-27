"""
UnifiedDataEngine Module

Defines the UnifiedDataEngine class that combines functionalities from DaskData and TorchData
to provide a unified interface for handling data.

Author: Lane
"""
import json
import os
import uuid
from typing import Type, Any, Dict, Tuple

import aiofiles
import dask.dataframe as dd
import pandas as pd
from numpy import dtype
from torch.utils.data import DataLoader

from research_analytics_suite.analytics.core.AnalyticsCore import AnalyticsCore
from research_analytics_suite.utils.Config import Config
from research_analytics_suite.data_engine.core.DaskData import DaskData
from research_analytics_suite.data_engine.memory.DataCache import DataCache
from research_analytics_suite.data_engine.data_streams.DataTypeDetector import DataTypeDetector
from research_analytics_suite.data_engine.core.TorchData import TorchData
from research_analytics_suite.data_engine.data_streams.BaseInput import BaseInput
from research_analytics_suite.utils.CustomLogger import CustomLogger


def flatten_json(y: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flattens a nested JSON dictionary.

    Args:
        y (Dict[str, Any]): The JSON dictionary to flatten.

    Returns:
        Dict[str, Any]: The flattened JSON dictionary.
    """
    out = {}

    def flatten(x: Any, name: str = ''):
        if isinstance(x, dict):
            for a in x:
                flatten(x[a], name + a + '_')
        elif isinstance(x, list):
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out


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
    _GENERATED_ID = None

    def __init__(self, backend='dask', dask_client=None, data=None, data_name=None):
        """
        Initializes the UnifiedDataEngine instance.

        Args:
            backend (str): The backend to use ('dask' or 'torch'). Default is 'dask'.
            dask_client: Dask client instance. Default is None.
            data: The data point. Default is None.
        """
        self._GENERATED_ID = uuid.uuid4()
        self.data = data
        self.data_name = f"{data_name}" if data_name else f"data_{uuid.uuid4().hex[:4]}"
        self.backend = backend
        self._logger = CustomLogger()
        self._config = Config()
        self.dask_client = dask_client  # Pointer to primary Dask client
        self.analytics = AnalyticsCore()  # Initialize AnalyticsCore Engine

        from research_analytics_suite.data_engine.Workspace import Workspace
        self._workspace = Workspace()

        self.dask_data = DaskData(data)
        self.torch_data = TorchData(data)
        self.data_cache = DataCache()  # Initialize DataCache
        self.live_input_source = None  # Initialize live input source
        self.engine_id = f"{uuid.uuid4()}"

    def __getstate__(self):
        state = self.__dict__.copy()
        state['_GENERATED_ID'] = None
        state['_logger'] = None
        state['_config'] = None
        state['data_cache'] = None
        state['dask_client'] = None
        state['live_input_source'] = None
        state['_cache'] = None
        state['analytics'] = None
        state['torch_data'] = None
        state['dask_data'] = None
        state['_workspace'] = None
        state['live_data_handler'] = None
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._GENERATED_ID = uuid.uuid4()
        self._logger = CustomLogger()
        self._config = Config()
        self.data_cache = DataCache()

        from research_analytics_suite.data_engine.Workspace import Workspace
        self._workspace = Workspace()

        self.live_input_source = None
        self.analytics = AnalyticsCore()
        self.torch_data = TorchData(self.data)
        self.dask_data = DaskData(self.data)

    @property
    def runtime_id(self) -> str:
        """
        Returns the runtime ID of the UnifiedDataEngine instance.

        Returns:
            str: The runtime ID.
        """
        return f"e-{self.engine_id[:4]}_{self._GENERATED_ID}"

    @property
    def short_id(self) -> str:
        """
        Returns the short ID of the UnifiedDataEngine instance.

        Returns:
            str: The short ID.
        """
        return f"{self.data_name}_{self.engine_id[:4]}"

    def detect_data_row(self, file_path, data_type):
        def is_numerical(_row):
            return all(self.is_number(_cell) for _cell in _row)

        if data_type == 'csv':
            with open(file_path, 'r') as f:
                for i, line in enumerate(f):
                    row = line.strip().split(',')
                    if is_numerical(row):
                        return i

        elif data_type == 'json':
            return 0

        elif data_type == 'parquet':
            return 0

        elif data_type == 'hdf5':
            return 0

        elif data_type == 'excel':
            xls = pd.ExcelFile(file_path)
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                for i, row in df.iterrows():
                    if is_numerical(row):
                        return i

        raise ValueError(f"Unsupported data type: {data_type}")

    @staticmethod
    def is_number(value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def load_data(self, file_path, return_type='dict'):
        data_type = os.path.splitext(file_path)[1][1:]
        self._logger.info(f"Loading data from {file_path} as {data_type}")

        try:
            if data_type == 'csv':
                data = dd.read_csv(file_path)
            elif data_type == 'json':
                with open(file_path, 'r') as f:
                    json_data = json.load(f)
                    flattened_data = [flatten_json(json_data)]
                    pandas_df = pd.DataFrame(flattened_data)
                    data = dd.from_pandas(pandas_df, npartitions=1)
            elif data_type == 'parquet':
                data = dd.read_parquet(file_path)
            elif data_type == 'hdf5':
                data = dd.read_hdf(file_path)
            elif data_type == 'excel':
                pandas_df = pd.read_excel(file_path)
                data = dd.from_pandas(pandas_df, npartitions=1)
            else:
                raise ValueError(f"Unsupported data type: {data_type}")

            if isinstance(data, dd.DataFrame):
                data = data.compute()

            if return_type == 'dict':
                data = data.to_dict()
            elif return_type != 'dataframe':
                raise ValueError(f"Unsupported return type: {return_type}")

            return data

        except FileNotFoundError:
            self._logger.error(Exception(f"File not found: {file_path}"), self)
            raise
        except Exception as e:
            self._logger.error(Exception(f"Error loading data from {file_path}: {e}"), self)
            raise

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

    async def save_engine(self, instance_path):
        engine_path = os.path.join(instance_path, self._config.ENGINE_DIR, self.engine_id)
        os.makedirs(engine_path, exist_ok=True)
        data_path = os.path.join(instance_path, 'data')
        os.makedirs(data_path, exist_ok=True)
        data_file_path = os.path.join(data_path, f"{self.data_name}.joblib")

        self._logger.info(f"Saving engine to {engine_path}")

        # Save data
        async with aiofiles.open(data_file_path, 'w') as data_file:
            await data_file.write(json.dumps(self.data))

        # Save metadata
        metadata = {
            'data_name': self.data_name,
            'backend': self.backend,
            'engine_id': self.engine_id,
        }
        async with aiofiles.open(os.path.join(f"{engine_path}", "metadata.json"), 'w') as metadata_file:
            await metadata_file.write(json.dumps(metadata))

        # Save a pickleable state of the engine
        engine_state = self.__getstate__()
        async with aiofiles.open(os.path.join(f"{engine_path}", 'engine_state.joblib'), 'w') as state_file:
            await state_file.write(json.dumps(engine_state))

        self._logger.info(f"Engine saved to {instance_path}")

    @staticmethod
    async def load_engine(instance_path, engine_id):
        engine_path = os.path.join(instance_path, 'engine', engine_id)

        # Load metadata
        async with aiofiles.open(os.path.join(f"{engine_path}", 'metadata.json'), 'r') as metadata_file:
            metadata = json.loads(await metadata_file.read())

        data_path = os.path.join(instance_path, 'data', f"{metadata['data_name']}.joblib")

        # Load data
        async with aiofiles.open(data_path, 'r') as data_file:
            data = json.loads(await data_file.read())

        # Load engine state
        async with aiofiles.open(os.path.join(f"{engine_path}", 'engine_state.joblib'), 'r') as state_file:
            engine_state = json.loads(await state_file.read())

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

    def apply(self, action):
        """
        Applies a function to the data.

        Args:
            action (function): The function to apply to the data.
        """
        if self.backend == 'dask':
            self.dask_data.apply(action)
        elif self.backend == 'torch':
            self.torch_data = TorchData(action(self.torch_data.get_data()))

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
        data.pop('_logger', None)
        data.pop('dask_client', None)
        data.pop('live_input_source', None)
        return data

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

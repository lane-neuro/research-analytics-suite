"""
data_engine package

This package provides the core functionality for handling data using Dask and PyTorch,
managing metadata, caching data, and integrating live data input sources.

Modules:
    base_data.py - Base class for handling single data points.
    dask_data.py - Dask extension for handling data.
    data_cache.py - Data caching mechanism.
    live_input/ - Subpackage for handling live data input sources.
    metadata.py - Class for storing metadata for data engines.
    torch_data.py - PyTorch extension for handling data.
    unified_data_engine.py - Unified data engine combining Dask and PyTorch functionalities.
    workspace.py - Workspace class to manage multiple data engines.
"""
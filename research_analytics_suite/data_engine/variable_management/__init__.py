"""
Variable Management Package

This package manages user-defined variables within the workspace using different storage backends.

Author: Lane
"""

from research_analytics_suite.data_engine.variable_management.UserVariablesManager import UserVariablesManager
from research_analytics_suite.data_engine.variable_management.storage.SQLiteStorage import SQLiteStorage
from research_analytics_suite.data_engine.variable_management.storage.MemoryStorage import MemoryStorage

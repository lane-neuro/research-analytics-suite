"""
Module for saving the active project in the NeuroBehavioral Analytics Suite.

This module defines the function for saving the active project to a file. It uses the DataEngine object to access the
project func and the pickle module to serialize the DataEngine object and write it to a file.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

from neurobehavioral_analytics_suite.data_engine import DataEngine
import pickle


def save_project(d_engine: DataEngine):
    """
    Saves the active project to a file.

    This function opens or creates a file at the root directory of the project, uses pickle to encode
    and write the DataEngine object to the file, and returns the file path as a string.

    Args:
        d_engine (DataEngine): The base/root DataEngine for the active project.

    Returns:
        str: Path to the new project configuration file.

    Example:
        ->> save_project(d_engine)
        'G:\\Projects\\Project.json'
    """

    # Opens/Creates a file at the root directory of the project
    file_path = d_engine.meta.base_dir + d_engine.meta.username + '-PROJECT_CONFIG.json'
    with open(file_path, 'wb') as file:
        # Use pickle to encode & write DataEngine object to file, return file path as string
        pickle.dump(d_engine, file)

    return file_path

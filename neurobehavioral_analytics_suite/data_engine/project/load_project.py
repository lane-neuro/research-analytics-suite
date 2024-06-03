"""
load_project.py

This modules defines the function to load a project from a given file path. It uses the pickle modules to decode the
DataEngine object from the file and returns it.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

import pickle


def load_project(file_in: str):
    """
    Loads the active project from a file.

    This function opens the file at the given path, uses pickle to decode the DataEngine object from
    the file, and returns the DataEngine object.

    Args:
        file_in (str): Path to the project configuration file (.json).

    Returns:
        DataEngine: A DataEngine object containing the active project func.

    Example:
        ->> load_project('G:\\Projects\\Project.json')
        <DataEngine object at 0x10d8cd160>
    """

    with open(file_in, 'rb') as file:
        # Use pickle to decode & return DataEngine object from file
        return pickle.load(file)

"""
Module for creating a new project in the NeuroBehavioral AnalyticsCore Suite.

This module defines the function to create a new project, save it to disk, reload it, and return it as a DataEngine
object. It uses the DataEngine class to initialize the base object and the save_project and load_project functions to
handle the saving and loading of the project.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

from neurobehavioral_analytics_suite.data_engine.project.load_project import load_project
from neurobehavioral_analytics_suite.data_engine.project.save_project import save_project
from neurobehavioral_analytics_suite.data_engine.DataEngine import DataEngine


def new_project(dir_in: str, user_in: str, subject_in: str, framerate_in: int, csv_path: str, logger):
    """
    Creates a new project, saves it to disk, reloads, and returns it as a project object.

    This function initializes the base DataEngine object with the provided parameters, saves the project
    to disk, and then reloads and returns the project as a DataEngine object.

    Args:
        dir_in (str): Directory where project files will be located on local disk.
        user_in (str): Name of user/experimenter.
        subject_in (str): Name of the subject of experiment (e.g., mouse, human, rat, etc.).
        framerate_in (int): Camera framerate.
        csv_path (str): Path where initial csv file is located on local disk.

    Returns:
        DataEngine: A DataEngine object containing the active project func.

    Example:
        ->> new_project('Z:\\your-project-directory\\',
                'Your_Name',
                'Subject_ID',
                60,
                'C:\\your-func-directory\\one-csv-file.csv'
            )
        <DataEngine object at 0x10d8cd160>
    """

    # Initialize the base DataEngine object
    base_engine = DataEngine(dir_in, user_in, subject_in, framerate_in, csv_path)
    base_engine.attach_logger(logger)
    base_engine.extract_csv()

    # Save the project to disk & return the loaded project
    save_file = save_project(base_engine.get_pickleable_data())
    return load_project(save_file)

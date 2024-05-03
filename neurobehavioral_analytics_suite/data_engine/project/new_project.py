"""
This module creates a new project, saves it to disk, reloads, & returns it as a project object.
"""

__author__ = 'Lane'
__copyright__ = 'Lane'
__credits__ = ['Lane']
__license__ = 'BSD 3-Clause License'
__version__ = '0.0.0.1'
__maintainer__ = 'Lane'
__emails__ = 'justlane@uw.edu'
__status__ = 'Prototype'

from neurobehavioral_analytics_suite.data_engine.project.load_project import load_project
from neurobehavioral_analytics_suite.data_engine.project.save_project import save_project
from neurobehavioral_analytics_suite.data_engine.DataEngine import DataEngine


def new_project(dir_in: str, user_in: str, subject_in: str, framerate_in: int, csv_path: str):
    """
    Creates a new project, saves it to disk, reloads, & returns it as a project object.

    Parameters
    ----------
    dir_in : str
        Directory where project files will be located on local disk.

    user_in: str
        Name of user/experimenter

    subject_in: str
        Name of the subject of experiment (e.g., mouse, human, rat, etc.)

    framerate_in: int
        Camera framerate

    csv_path: str
        Path where initial csv file is located on local disk.

    Returns
    -------
    DataEngine
        A DataEngine object containing the active project data.

    Example
    -------
    ->> new_project(\'Z:\\your-project-directory\\',
            'Your_Name',
            'Subject_ID',
            60,
            \'C:\\your-data-directory\\one-csv-file.csv\'
        )

    """

    # Initialize the base DataEngine object
    base_engine = DataEngine(dir_in, user_in, subject_in, framerate_in, csv_path)

    # Save the project to disk & return the loaded project
    save_file = save_project(base_engine)
    return load_project(save_file)


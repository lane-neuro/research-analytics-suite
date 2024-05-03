"""
This module loads project data from the supplied file path.
"""

__author__ = 'Lane'
__copyright__ = 'Lane'
__credits__ = ['Lane']
__license__ = 'BSD 3-Clause License'
__version__ = '0.0.0.1'
__maintainer__ = 'Lane'
__emails__ = 'justlane@uw.edu'
__status__ = 'Prototype'


def load_project(file_in: str):
    """
    Loads the active project to a file.

    Parameters
    ----------
    file_in: str
        Path to the project config file (.json)

    Examples
    --------
    Project will be loaded from a file.
    ->> load_project(\'G:\\Projects\\Project.json\')

    """

    file = open(file_in, 'rb')

    # Unpack & return project object
    import pickle
    return pickle.load(file)

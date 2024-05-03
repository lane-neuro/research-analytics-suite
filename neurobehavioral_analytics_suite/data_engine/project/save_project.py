"""
This module saves the active project to a file.
"""

__author__ = 'Lane'
__copyright__ = 'Lane'
__credits__ = ['Lane']
__license__ = 'BSD 3-Clause License'
__version__ = '0.0.0.1'
__maintainer__ = 'Lane'
__emails__ = 'justlane@uw.edu'
__status__ = 'Prototype'

from neurobehavioral_analytics_suite.data_engine import DataEngine


def save_project(d_engine: DataEngine):
    """
    Saves the active project to a file.

    Parameters
    ----------
    d_engine: DataEngine
        The base/root DataEngine for the active project.

    Returns
    -------
    str
        Path to the new project configuration file

    Examples
    --------
    ->> save_project(d_engine)

    """

    # Opens/Creates a file at the root directory of the project
    file = open(d_engine.meta.base_dir + d_engine.meta.username + '-PROJECT_CONFIG.json', 'wb')

    # Use pickle to encode & write DataEngine object to file, return file path as string
    import pickle
    pickle.dump(d_engine, file)
    return d_engine.meta.base_dir + d_engine.meta.username + '-PROJECT_CONFIG.json'

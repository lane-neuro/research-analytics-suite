"""
This class is designed to store project metadata for the active project.
"""

__author__ = 'Lane'
__copyright__ = 'Lane'
__credits__ = ['Lane']
__license__ = 'BSD 3-Clause License'
__version__ = '0.0.0.1'
__maintainer__ = 'Lane'
__emails__ = 'justlane@uw.edu'
__status__ = 'Prototype'

from neurobehavioral_analytics_suite.analytics import Analytics


class ProjectMetadata(object):

    def __init__(self, directory_in: str, user_in: str, subject_in: str, framerate_in: int,
                 analytics_in: Analytics):

        self.analytics = analytics_in               # pointer to Analytics engine

        self.base_dir = directory_in                # root directory for project

        self.username = user_in                     # name of current experimenter / researcher
        self.subject = subject_in                   # name of subject (i.e., 'mouse-2', 'CB6', etc.)

        self.body_parts_count = 0                   # number of body parts in pixel-tracking data
        self.framerate = framerate_in               # framerate of the camera
        self.start_index = 0                        # first frame index of relevant data
        self.end_index = 0                          # final frame index of relevant data

        print(f"Metadata storage initialized...")

    def __repr__(self):
        # Returns a string of summary data of the object

        return (f"ProjectMetadata:(Animal: \'{self.subject}\', Number of Body Parts: {self.body_parts_count}, "
                f"Framerate:{self.framerate}fps)")


"""
A class for storing positional data from xy-coordinate tracking datasets.

Typical usage example:
    pose = PoseData(project_metadata, csv_path, use_likelihood{bool})
    pose.extract_csv()
    print(pose.pack())                  # Formats data for console output

"""

__author__ = 'Lane'
__copyright__ = 'Lane'
__credits__ = ['Lane']
__license__ = 'BSD 3-Clause License'
__version__ = '0.0.0.1'
__maintainer__ = 'Lane'
__emails__ = 'justlane@uw.edu'
__status__ = 'Prototype'

import csv
from copy import deepcopy
from neurobehavioral_analytics_suite.data_engine.d_structs.SingleFrame import SingleFrame
from neurobehavioral_analytics_suite.data_engine.project import ProjectMetadata


class PoseData(object):
    def __init__(self, meta: ProjectMetadata, csv_path: str, use_likelihood):

        self.use_likelihood = use_likelihood            # Whether to check for p-value
        self.meta = meta                                # Binds with ProjectMetadata
        self.csv_path = csv_path
        self.frames = []
        print(f"PoseData object initialized")

    def __repr__(self):
        return f"PoseData:(\'{self.pack()}\')"

    def pack(self):
        """
        Formats data for console output

        Returns
        -------
        str
            Formatted output

        """

        pose_out = ""
        if self.meta.end_index == 0:
            for iframe in self.frames:
                rounded_frame = self.round_frame(iframe)
                frame_str = "~"
                for coord in rounded_frame.coords:
                    if self.use_likelihood:
                        frame_str += f"{coord.x}_{coord.y}_{coord.likelihood},"
                    else:
                        frame_str += f"{coord.x}_{coord.y},"
                pose_out += frame_str.rstrip(',')  # Remove trailing comma if present
        else:
            # TODO
            pass
        return pose_out

    def round_frame(self, frame):
        # Create a deep copy so that the original data isn't modified
        rounded_frame = deepcopy(frame)
        for coord in rounded_frame.coords:
            coord.x = round(coord.x, 3)
            coord.y = round(coord.y, 3)
            if self.use_likelihood:
                coord.likelihood = round(coord.likelihood, 3)
            else:
                coord.likelihood = None  # You can set it to None or just not store it at all.
        return rounded_frame

    def extract_csv(self):
        with open(self.csv_path, mode='r') as file:
            csv_file = csv.reader(file)

            for i, row in enumerate(csv_file, -3):
                if self.meta.body_parts_count == 0:
                    self.meta.body_parts_count = (len(row) - 1) / (3 if self.use_likelihood else 2)
                if i >= 0:
                    self.frames.extend([SingleFrame(self.use_likelihood, row[:])])
        print(
            f"PoseData: \'{self.meta.subject}\' .csv file extracted for {self.meta.body_parts_count} coordinates across {len(self.frames)} frames.")

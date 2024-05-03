"""
A class to hold all data related to a single frame.
"""

__author__ = 'Lane'
__copyright__ = 'Lane'
__credits__ = ['Lane']
__license__ = 'BSD 3-Clause License'
__version__ = '0.0.0.1'
__maintainer__ = 'Lane'
__emails__ = 'justlane@uw.edu'
__status__ = 'Prototype'

from copy import deepcopy
from .. import DataEngine
from .Coord2D import Coord2D


class SingleFrame(object):
    def __init__(self, use_likelihood, *data_in):
        self.use_likelihood = use_likelihood
        row = []
        for jj in data_in:
            row.extend(jj)
        self.frame_num = row[0]
        self.coords = []

        step = 3
        for ii in range(1, len(row), step):
            if self.use_likelihood:
                self.coords.extend([Coord2D(row[ii], row[ii + 1], row[ii + 2])])
            else:
                self.coords.extend([Coord2D(row[ii], row[ii + 1])])

    def __repr__(self):
        frame_out = ""

        for coord in self.coords:
            frame_out = f"{frame_out},{repr(coord)}"
        return f"{frame_out}"

    def transform(self, engine: DataEngine):
        new_frame = deepcopy(self)  # Create a new frame object
        for coord in new_frame.coords:
            coord.transform(engine)
        return new_frame

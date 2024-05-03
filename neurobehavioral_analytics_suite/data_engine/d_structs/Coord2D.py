"""
A class dedicated to handling 2D coordinates.
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
from neurobehavioral_analytics_suite.data_engine import DataEngine


class Coord2D(object):

    def __init__(self, x_in: float, y_in: float, likelihood_in: float = None):
        self.x = float(x_in)
        self.y = float(y_in)
        self.likelihood = float(likelihood_in) if likelihood_in else None

    def formatted_str(self):
        if self.likelihood is not None:
            return f"{self.x}_{self.y}_{self.likelihood}"
        else:
            return f"{self.x}_{self.y}"

    def __repr__(self):
        if self.likelihood is not None:
            return f"{self.x}_{self.y}_{self.likelihood}"
        else:
            return f"{self.x}_{self.y}"

    def transform(self, engine: DataEngine):
        new_datapoint = deepcopy(self)  # Create a new data point object
        return engine.transform(new_datapoint)

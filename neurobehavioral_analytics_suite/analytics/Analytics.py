"""
Analytical Engine to process neurobehavioral data from NBAS-DataEngine.
"""

__author__ = 'Lane'
__copyright__ = 'Lane'
__credits__ = ['Lane']
__license__ = 'BSD 3-Clause License'
__version__ = '0.0.0.1'
__maintainer__ = 'Lane'
__emails__ = 'justlane@uw.edu'
__status__ = 'Prototype'


class Analytics(object):

    def __init__(self, transformations=None):
        if transformations is None:
            self.transformations = []
        else:
            self.transformations = transformations
        print("Analytics Engine started")

    def transform(self, datapoint):
        for transformation in self.transformations:
            datapoint = transformation.transform(datapoint)
        return datapoint

    def add_transformation(self, transformation):
        self.transformations.append(transformation)

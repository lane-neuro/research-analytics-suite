__author__ = 'Lane'
__copyright__ = 'Lane'
__credits__ = ['Lane']
__license__ = 'BSD 3-Clause License'
__version__ = '0.0.0.1'
__maintainer__ = 'Lane'
__emails__ = 'justlane@uw.edu'
__status__ = 'Prototype'


class ScaleTransform:

    def __init__(self, scale):
        self.scale = scale

    def __repr__(self):
        return f"ScaleTransform, scalar = {self.scale}"

    def transform(self, datapoint):
        datapoint.x *= self.scale
        datapoint.y *= self.scale
        return datapoint

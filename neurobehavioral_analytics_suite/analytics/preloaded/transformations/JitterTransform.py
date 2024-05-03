__author__ = 'Lane'
__copyright__ = 'Lane'
__credits__ = ['Lane']
__license__ = 'BSD 3-Clause License'
__version__ = '0.0.0.1'
__maintainer__ = 'Lane'
__emails__ = 'justlane@uw.edu'
__status__ = 'Prototype'

import numpy as np


class JitterTransform:

    def __init__(self, jitter_strength=0.1):
        self.jitter_strength = jitter_strength

    def __repr__(self):
        return f"JitterTransform, jitter_strength = {self.jitter_strength}"

    def transform(self, datapoint):
        datapoint.x += np.random.uniform(-self.jitter_strength, self.jitter_strength)
        datapoint.y += np.random.uniform(-self.jitter_strength, self.jitter_strength)
        return datapoint

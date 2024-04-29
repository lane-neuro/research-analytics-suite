#! python
# -*- coding: utf-8 -*-

__author__ = 'Lane'
__copyright__ = 'Lane'
__credits__ = ['Lane']
__license__ = 'BSD 3-Clause License'
__version__ = '0.0.0.1'
__maintainer__ = 'Lane'
__emails__ = 'justlane@uw.edu'
__status__ = 'Prototype'

"""
Docstring
"""


class TranslateTransform:

    def __init__(self, delta_x, delta_y):
        self.delta_x = delta_x
        self.delta_y = delta_y

    def __repr__(self):
        return f"TranslateTransform, x,y = ({self.delta_x}, {self.delta_y})"

    def transform(self, datapoint):
        datapoint.x += self.delta_x
        datapoint.y += self.delta_y
        return datapoint

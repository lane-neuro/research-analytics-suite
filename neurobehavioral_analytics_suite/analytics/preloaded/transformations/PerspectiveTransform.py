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


class PerspectiveTransform:

    def __init__(self, perspective_coeff=0.0001):
        self.perspective_coeff = perspective_coeff

    def __repr__(self):
        return f"PerspectiveTransform, perspective_coeff = {self.perspective_coeff}"

    def transform(self, datapoint):
        scale = 1.0 + self.perspective_coeff * datapoint.y
        datapoint.x *= scale
        datapoint.y *= scale
        return datapoint

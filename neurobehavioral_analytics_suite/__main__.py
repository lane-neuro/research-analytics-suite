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

# Imports
import sys


def main():
    print('Starting NeuroBehavioral Analytics Suite v' + __version__)
    from neurobehavioral_analytics_suite.data_engine import data_engine


if __name__ == '__main__':
    sys.exit(main())

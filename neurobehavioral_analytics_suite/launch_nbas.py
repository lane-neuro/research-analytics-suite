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
import os
import sys
import logging


def launch_nbas():
    from neurobehavioral_analytics_suite.data_engine.data_engine import start_data_engine
    d_engine = start_data_engine()

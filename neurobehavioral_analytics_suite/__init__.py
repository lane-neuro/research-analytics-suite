#! python
# -*- coding: utf-8 -*-

"""
Docstring
"""

__author__ = 'Lane'
__copyright__ = 'Lane'
__credits__ = ['Lane']
__license__ = 'BSD 3-Clause License'
__version__ = '0.0.0.1'
__maintainer__ = 'Lane'
__emails__ = 'justlane@uw.edu'
__status__ = 'Prototype'

# Imports
import os

DEBUG = True and "DEBUG" in os.environ["DEBUG"]

print(f"Loading NBAS {__version__}...")

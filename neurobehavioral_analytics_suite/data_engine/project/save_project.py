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

import pickle
from . import ProjectMetadata

"""
Docstring
"""


def save_project(b_engine):
    file = open(b_engine.meta.BASE_DIR + b_engine.meta.username + '-PROJECT_CONFIG.json', 'wb')
    pickle.dump(b_engine, file)
    return b_engine.meta.BASE_DIR + b_engine.meta.username + '-PROJECT_CONFIG.json'

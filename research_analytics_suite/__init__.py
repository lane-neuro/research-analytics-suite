"""
Research Analytics Suite (RAS)
=========================

This package is designed to provide a set of tools for managing and executing operations, as well as storing and
managing data produced by those operations. The suite is designed to be modular and extensible, allowing for easy
integration with existing codebases and systems.

"""

__author__ = 'Lane'
__copyright__ = 'Lane'
__credits__ = ['Lane']
__license__ = 'BSD 3-Clause License'
__version__ = '0.0.0.1'
__maintainer__ = 'Lane'
__emails__ = 'justlane@uw.edu'
__status__ = 'Prototype'

import os
import shutil
import sys
import warnings

from .ResearchAnalyticsSuite import ResearchAnalyticsSuite


def get_console_size():
    try:
        size = shutil.get_terminal_size()
        return size.columns, size.lines
    except OSError:
        return 80, 24


warnings.filterwarnings('ignore', category=FutureWarning)


CONSOLE_WIDTH, CONSOLE_HEIGHT = get_console_size()

# Disable OneDNN optimizations for TensorFlow
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Disable OneDNN optimizations for PyTorch
os.environ['TORCH_DNNL_DISABLE_FUSE'] = '1'

# Set python path for the package
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

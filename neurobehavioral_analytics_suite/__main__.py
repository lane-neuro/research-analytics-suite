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

import sys
from neurobehavioral_analytics_suite.launch_nbas import launch_nbas

"""
Docstring
"""


def main():
    print('Starting NeuroBehavioral Analytics Suite v' + __version__)
    launch_nbas()


if __name__ == '__main__':
    sys.argv = ['__main__.py',
                '-u', 'dev_test',
                '-d', '..\\..\\NBAS-test-output\\',
                '-s', 'Mouse',
                '-c', '60',
                '-f',
                '..\\sample_datasets\\2024-Tariq-et-al_olfaction\\9-2-2021-4-07 PM-Mohammad-ETHSensor-CB5-28_reencodedDLC_resnet50_odor-arenaOct3shuffle1_200000_filtered.csv']
    main()

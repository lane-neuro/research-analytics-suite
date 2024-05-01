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

"""
Docstring
"""


def main():
    print('Starting NeuroBehavioral Analytics Suite v' + __version__)
    from neurobehavioral_analytics_suite.launch_nbas import launch_nbas
    launch_nbas()


if __name__ == '__main__':
    sys.argv = ['__main__.py', '-u', 'Lane', '-d', 'C:\\Users\\lane\\Documents\\NBAS-Testing\\', '-s', 'Mouse', '-c', '60',
                '-f', 'C:\\Users\\lane\\Documents\\NBAS-Testing\\examples\\9-2-2021-4-07 PM-Mohammad-ETHSensor-CB5-28_reencodedDLC_resnet50_odor-arenaOct3shuffle1_200000_filtered.csv']
    main()

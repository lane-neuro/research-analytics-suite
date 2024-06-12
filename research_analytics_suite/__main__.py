"""
This module serves as the main entry point for running the Research Analytics Suite.

It contains the main function which initiates the suite and sets up the necessary parameters.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import asyncio
import sys

from research_analytics_suite.launch_ras import launch_ras


def main():
    """
    Initiates the Research Analytics Suite.

    This function prints the version of the suite, imports the launch_ras module,
    and calls it to start the suite.
    """
    print('Starting Research Analytics Suite v0.0.0.1')
    try:
        asyncio.run(launch_ras())
    except KeyboardInterrupt:
        print('Exiting Research Analytics Suite...')
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Exiting Research Analytics Suite...")
    finally:
        print("Cleaning up...")
        asyncio.get_event_loop().close()
        sys.exit(0)


if __name__ == '__main__':
    sys.argv = ['__main__.py',
                '-o', "C:\\Users\\lane\\Documents\\RAS Workspaces\\default_workspace\\config.json",
                '-g', 'True',
                '-u', 'dev_test',
                '-d', '..\\..\\RAS-test-output\\',
                '-s', 'Mouse',
                '-c', '60',
                '-f', '..\\sample_datasets\\2024-Tariq-et-al_olfaction\\9-2-2021-4-07 PM-Mohammad-ETHSensor-CB5-28_'
                      'reencodedDLC_resnet50_odor-arenaOct3shuffle1_200000_filtered.csv']
    main()

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

import nest_asyncio

from research_analytics_suite.RASLauncher import RASLauncher


def main():
    """
    Initiates the Research Analytics Suite.
    """
    try:
        # Apply nest_asyncio to allow asyncio to run in Jupyter notebooks
        nest_asyncio.apply()

        # Run the Research Analytics Suite
        asyncio.run(RASLauncher())

    except KeyboardInterrupt:
        print('Exiting Research Analytics Suite..')

    except Exception as e:
        print(f"Fatal error occurred: {e}")

    finally:
        print("Cleaning up..")
        asyncio.get_event_loop().close()
        sys.exit(0)


if __name__ == '__main__':
    sys.argv = ['__main__.py',
                '-o', 'default_workspace']
    main()

"""
This module contains the function for parsing command line arguments for launching the Research Analytics Suite.

Author: Lane
"""
import argparse
import os


def get_launch_args():
    """
    Parses command line arguments for launching the Research Analytics Suite.

    The arguments include options for opening an existing workspace, creating a new workspace, and specifying various
    workspace parameters.

    Returns:
        argparse.ArgumentParser: The argument parser with the parsed command line arguments.
    """
    _parser = argparse.ArgumentParser()

    # GUI argument
    _parser.add_argument('-g', '--gui',
                         help='Launches the Research Analytics Suite GUI', default='True')

    # Open workspace arguments
    _parser.add_argument('-o', '--open_workspace',
                         help='Opens an existing workspace from the specified folder/directory')
    _parser.add_argument('-c', '--config',
                         help='Path to the configuration file for the workspace')

    # New workspace arguments
    _parser.add_argument('-d', '--directory',
                         help='Directory where workspace files will be located',
                         default=os.path.expanduser(f"~/Research-Analytics-Suite/workspaces/"))
    _parser.add_argument('-n', '--name',
                         help='Name of the new workspace')

    return _parser

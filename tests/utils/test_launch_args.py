import os
import pytest
from unittest.mock import patch

from research_analytics_suite.utils.launch_args import get_launch_args


@pytest.fixture
def parser():
    return get_launch_args()


def test_default_args(parser):
    test_args = []
    with patch('sys.argv', ['test'] + test_args):
        args = parser.parse_args()
        assert args.gui == 'True'
        assert args.open_workspace is None
        assert args.config is None
        assert args.directory == os.path.expanduser("~/Research-Analytics-Suite/workspaces/")
        assert args.name is None


def test_open_workspace(parser):
    test_args = ['-o', 'workspace_folder']
    with patch('sys.argv', ['test'] + test_args):
        args = parser.parse_args()
        assert args.gui == 'True'
        assert args.open_workspace == 'workspace_folder'
        assert args.config is None
        assert args.directory == os.path.expanduser("~/Research-Analytics-Suite/workspaces/")
        assert args.name is None


def test_new_workspace(parser):
    test_args = ['-d', '/custom/workspace/dir', '-n', 'NewWorkspace']
    with patch('sys.argv', ['test'] + test_args):
        args = parser.parse_args()
        assert args.gui == 'True'
        assert args.open_workspace is None
        assert args.config is None
        assert args.directory == '/custom/workspace/dir'
        assert args.name == 'NewWorkspace'


def test_with_config(parser):
    test_args = ['-c', 'config.yaml']
    with patch('sys.argv', ['test'] + test_args):
        args = parser.parse_args()
        assert args.gui == 'True'
        assert args.open_workspace is None
        assert args.config == 'config.yaml'
        assert args.directory == os.path.expanduser("~/Research-Analytics-Suite/workspaces/")
        assert args.name is None

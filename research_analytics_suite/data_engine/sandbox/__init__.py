"""
Sandbox Module

Provides isolated workspace environments for safe operation testing and execution.
The sandbox creates read-only mirrors of real workspaces, allowing AI/ML systems
to experiment with operations without risking user data.

Key Components:
- SandboxWorkspace: Isolated, read-only workspace mirror
- WorkspaceCloner: Handles cloning logic from real to sandbox
- ExecutionIsolator: Ensures operations cannot affect real workspace

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Development
"""

from research_analytics_suite.data_engine.sandbox.SandboxWorkspace import SandboxWorkspace
from research_analytics_suite.data_engine.sandbox.WorkspaceCloner import WorkspaceCloner
from research_analytics_suite.data_engine.sandbox.ExecutionIsolator import ExecutionIsolator

__all__ = [
    'SandboxWorkspace',
    'WorkspaceCloner',
    'ExecutionIsolator',
]

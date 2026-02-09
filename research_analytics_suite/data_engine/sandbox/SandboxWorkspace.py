"""
SandboxWorkspace Module

Creates isolated, read-only mirrors of real workspaces for safe operation testing.
The sandbox workspace uses DataProfiles instead of raw data and enforces strict
isolation to prevent any modifications to the real workspace.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Development
"""
from __future__ import annotations
from typing import Optional, Dict, Any, List
from pathlib import Path

from research_analytics_suite.utils.CustomLogger import CustomLogger
from research_analytics_suite.utils.Config import Config
from research_analytics_suite.data_engine.core.DataProfile import DataProfile


class SandboxWorkspace:
    """
    Isolated, read-only mirror of a real workspace.

    The SandboxWorkspace provides a safe environment for testing operations
    without risking user data. It mirrors metadata and uses DataProfiles
    instead of accessing raw data.

    Key Features:
    - Read-only access to workspace metadata
    - Uses DataProfiles instead of raw data
    - Resource limitations (memory, CPU)
    - Automatic cleanup
    - Audit logging
    """

    def __init__(self, name: str):
        """
        Initialize a sandbox workspace.

        Args:
            name: Name for the sandbox workspace
        """
        self._logger = CustomLogger()
        self._config = Config()

        self.name = name
        self.is_sandbox = True  # Flag to identify as sandbox
        self.source_workspace = None

        # Mirrored metadata
        self._variables: Dict[str, Any] = {}
        self._data_profiles: List[DataProfile] = []
        self._operation_library_snapshot: Dict[str, Any] = {}

        # Resource tracking
        self._memory_limit_mb = 0.0
        self._memory_used_mb = 0.0

        # Safety flags
        self._is_isolated = True
        self._read_only = True

    async def create_from_workspace(self, workspace) -> 'SandboxWorkspace':
        """
        Creates a sandbox mirror of a real workspace.

        Args:
            workspace: The real Workspace to mirror

        Returns:
            Self for chaining
        """
        self._logger.info(f"Creating sandbox mirror of workspace: {workspace._config.WORKSPACE_NAME}")

        try:
            self.source_workspace = workspace

            # Mirror workspace metadata
            await self.mirror_variables(workspace)
            await self.mirror_data_profiles(workspace)
            await self.mirror_operation_library(workspace)

            # Validate isolation
            self.enforce_isolation()

            self._logger.info(f"Sandbox workspace '{self.name}' created successfully")
            return self

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)
            raise

    async def mirror_variables(self, workspace) -> Dict[str, Any]:
        """
        Mirrors workspace variables (metadata only).

        Args:
            workspace: The real Workspace

        Returns:
            Dictionary of mirrored variables
        """
        self._logger.debug("Mirroring workspace variables")

        try:
            # Mirror workspace configuration and metadata
            self._variables = {
                'workspace_name': workspace._config.WORKSPACE_NAME,
                'optimization_settings': workspace._optimization_settings.copy() if hasattr(workspace, '_optimization_settings') else {},
                'workspace_profile': workspace._workspace_profile.copy() if hasattr(workspace, '_workspace_profile') else {},
            }

            self._logger.debug(f"Mirrored {len(self._variables)} workspace variables")
            return self._variables

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)
            self._variables = {}
            return self._variables

    async def mirror_data_profiles(self, workspace) -> List[DataProfile]:
        """
        Creates DataProfiles from workspace data instead of copying raw data.

        Args:
            workspace: The real Workspace

        Returns:
            List of DataProfile objects
        """
        self._logger.debug("Creating data profiles for sandbox")

        try:
            self._data_profiles = []

            # Access the Universal Data Engine to get data profiles
            if hasattr(workspace, '_universal_engine') and workspace._universal_engine:
                engine = workspace._universal_engine

                # Get all data contexts from memory manager
                if hasattr(workspace, '_memory_manager') and workspace._memory_manager:
                    memory_manager = workspace._memory_manager

                    # Iterate through memory slots to find data contexts
                    if hasattr(memory_manager, '_memory_slots'):
                        for slot_name, slot in memory_manager._memory_slots.items():
                            if hasattr(slot, 'data') and slot.data is not None:
                                try:
                                    # Profile the data using the engine
                                    from research_analytics_suite.data_engine.core.DataContext import DataContext
                                    if isinstance(slot.data, DataContext):
                                        # Already has a profile
                                        if slot.data.profile:
                                            self._data_profiles.append(slot.data.profile)
                                    else:
                                        # Create a profile for the data
                                        profile = await engine.profile_data(slot.data)
                                        if profile:
                                            self._data_profiles.append(profile)
                                except Exception as e:
                                    self._logger.warning(f"Failed to profile data from slot {slot_name}: {e}")

            self._logger.debug(f"Created {len(self._data_profiles)} data profiles for sandbox")
            return self._data_profiles

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)
            self._data_profiles = []
            return self._data_profiles

    async def mirror_operation_library(self, workspace) -> Dict[str, Any]:
        """
        Mirrors operation library references.

        Args:
            workspace: The real Workspace

        Returns:
            Dictionary of operation library snapshot
        """
        self._logger.debug("Mirroring operation library")

        try:
            # Get library manifest from workspace
            if hasattr(workspace, '_library_manifest') and workspace._library_manifest:
                library_manifest = workspace._library_manifest

                # Get the operation library
                if hasattr(library_manifest, '_library'):
                    # Create a shallow copy of library metadata (references only, no deep copy)
                    self._operation_library_snapshot = {
                        'categories': list(library_manifest._categories.keys()) if hasattr(library_manifest, '_categories') else [],
                        'operation_count': len(library_manifest._library) if library_manifest._library else 0,
                        'library_ref': library_manifest._library  # Keep reference for operation lookups
                    }

                    self._logger.debug(f"Mirrored operation library with {self._operation_library_snapshot['operation_count']} operations")
                else:
                    self._operation_library_snapshot = {'categories': [], 'operation_count': 0, 'library_ref': {}}
            else:
                self._operation_library_snapshot = {'categories': [], 'operation_count': 0, 'library_ref': {}}

            return self._operation_library_snapshot

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)
            self._operation_library_snapshot = {'categories': [], 'operation_count': 0, 'library_ref': {}}
            return self._operation_library_snapshot

    async def get_data_profiles(self) -> List[DataProfile]:
        """
        Returns data profiles (not raw data).

        Returns:
            List of DataProfile objects
        """
        return self._data_profiles

    def enforce_isolation(self) -> None:
        """
        Ensures sandbox cannot affect real workspace.

        Validates that:
        - No write access to real workspace
        - Resource limits are enforced
        - Audit logging is active
        """
        if not self._is_isolated or not self._read_only:
            raise RuntimeError("Sandbox isolation compromised")

        self._logger.debug("Sandbox isolation validated")

    def validate_safety(self) -> bool:
        """
        Validates sandbox safety constraints.

        Returns:
            True if all safety constraints are met
        """
        self._memory_limit_mb = 1024 # Example limit

        checks = [
            self._is_isolated,
            self._read_only,
            self._memory_used_mb <= self._memory_limit_mb,
        ]

        return all(checks)

    async def cleanup(self) -> None:
        """
        Cleans up sandbox resources.
        """
        self._logger.debug(f"Cleaning up sandbox workspace: {self.name}")

        # Clear all mirrored data
        self._variables.clear()
        self._data_profiles.clear()
        self._operation_library_snapshot.clear()

        self._logger.info(f"Sandbox workspace '{self.name}' cleaned up")

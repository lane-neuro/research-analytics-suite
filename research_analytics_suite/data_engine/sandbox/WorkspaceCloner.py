"""
WorkspaceCloner Module

Handles cloning logic from real workspaces to sandbox workspaces.
Implements selective cloning (metadata only) and efficient delta updates.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Development
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from research_analytics_suite.utils.CustomLogger import CustomLogger
from research_analytics_suite.data_engine.sandbox.SandboxWorkspace import SandboxWorkspace


class WorkspaceCloner:
    """
    Handles cloning logic from real to sandbox workspaces.

    Key Features:
    - Selective cloning (metadata only, no raw data)
    - Efficient shallow copying
    - Tracks cloning timestamps
    - Handles incremental updates
    - Validates cloning success
    """

    def __init__(self):
        """Initialize workspace cloner."""
        self._logger = CustomLogger()
        self._cloning_history: Dict[str, datetime] = {}

    async def clone_workspace(self, source_workspace, target_sandbox: SandboxWorkspace) -> None:
        """
        Clones workspace metadata to sandbox.

        Args:
            source_workspace: Real workspace to clone from
            target_sandbox: Sandbox workspace to clone into
        """
        self._logger.info(f"Cloning workspace to sandbox: {target_sandbox.name}")

        try:
            # Clone metadata only
            await self.clone_operation_library(source_workspace, target_sandbox)
            await self.clone_data_profiles(source_workspace, target_sandbox)
            await self.clone_variables(source_workspace, target_sandbox)

            # Record cloning timestamp
            self._cloning_history[target_sandbox.name] = datetime.now()

            # Validate cloning
            if not self._validate_clone(source_workspace, target_sandbox):
                raise RuntimeError("Clone validation failed")

            self._logger.info(f"Workspace cloned successfully to: {target_sandbox.name}")

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)
            raise

    async def clone_operation_library(self, source_workspace, target_sandbox: SandboxWorkspace) -> None:
        """
        Clones operation library references.

        Args:
            source_workspace: Real workspace
            target_sandbox: Sandbox workspace
        """
        self._logger.debug("Cloning operation library")

        try:
            # Use the sandbox's own mirror method
            await target_sandbox.mirror_operation_library(source_workspace)
            self._logger.debug("Operation library cloned successfully")

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)
            raise

    async def clone_data_profiles(self, source_workspace, target_sandbox: SandboxWorkspace) -> None:
        """
        Clones data profiles (not raw data).

        Args:
            source_workspace: Real workspace
            target_sandbox: Sandbox workspace
        """
        self._logger.debug("Cloning data profiles")

        try:
            # Use the sandbox's own mirror method which uses UniversalDataEngine
            profiles = await target_sandbox.mirror_data_profiles(source_workspace)
            self._logger.debug(f"Cloned {len(profiles)} data profiles successfully")

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)
            raise

    async def clone_variables(self, source_workspace, target_sandbox: SandboxWorkspace) -> None:
        """
        Clones workspace variables (metadata only).

        Args:
            source_workspace: Real workspace
            target_sandbox: Sandbox workspace
        """
        self._logger.debug("Cloning workspace variables")

        try:
            # Use the sandbox's own mirror method
            variables = await target_sandbox.mirror_variables(source_workspace)
            self._logger.debug(f"Cloned {len(variables)} workspace variables successfully")

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)
            raise

    async def sync_changes(self, changes: List[Dict[str, Any]], target_sandbox: SandboxWorkspace) -> None:
        """
        Syncs incremental changes to sandbox.

        Args:
            changes: List of change dictionaries to sync
            target_sandbox: Sandbox workspace to update
        """
        self._logger.debug(f"Syncing {len(changes)} changes to sandbox")

        try:
            for change in changes:
                change_type = change.get('type', 'unknown')

                if change_type == 'data_added':
                    # Re-profile new data
                    await self.clone_data_profiles(change.get('workspace'), target_sandbox)

                elif change_type == 'variable_updated':
                    # Re-clone variables
                    await self.clone_variables(change.get('workspace'), target_sandbox)

                elif change_type == 'operation_library_updated':
                    # Re-clone operation library
                    await self.clone_operation_library(change.get('workspace'), target_sandbox)

                else:
                    self._logger.warning(f"Unknown change type: {change_type}")

            # Update clone timestamp
            self._cloning_history[target_sandbox.name] = datetime.now()
            self._logger.debug(f"Synced {len(changes)} changes successfully")

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)
            raise

    def _validate_clone(self, source_workspace, target_sandbox: SandboxWorkspace) -> bool:
        """
        Validates that cloning was successful.

        Args:
            source_workspace: Real workspace
            target_sandbox: Sandbox workspace

        Returns:
            True if clone is valid
        """
        try:
            # Validate sandbox safety constraints
            if not target_sandbox.validate_safety():
                self._logger.error("Sandbox safety validation failed")
                return False

            # Validate that sandbox has expected metadata
            if not target_sandbox._variables:
                self._logger.warning("Sandbox has no variables - may be empty workspace")

            # Validate isolation flags
            if not target_sandbox._is_isolated or not target_sandbox._read_only:
                self._logger.error("Sandbox isolation flags incorrect")
                return False

            # Validate source reference
            if target_sandbox.source_workspace != source_workspace:
                self._logger.error("Sandbox source workspace reference mismatch")
                return False

            self._logger.debug("Clone validation passed")
            return True

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)
            return False

    def get_last_clone_time(self, sandbox_name: str) -> Optional[datetime]:
        """
        Gets timestamp of last clone operation.

        Args:
            sandbox_name: Name of sandbox workspace

        Returns:
            Timestamp of last clone, or None if never cloned
        """
        return self._cloning_history.get(sandbox_name)

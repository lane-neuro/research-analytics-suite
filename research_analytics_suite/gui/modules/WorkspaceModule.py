import asyncio
import os
import uuid
import dearpygui.dearpygui as dpg

from research_analytics_suite.utils.Config import Config
from research_analytics_suite.data_engine.Workspace import Workspace
from research_analytics_suite.operation_manager.control.OperationControl import OperationControl
from research_analytics_suite.utils.CustomLogger import CustomLogger


class WorkspaceModule:
    """A class to manage the GUI representation of the Workspace."""

    def __init__(self, width: int, height: int):
        """
        Initializes the WorkspaceModule with the given workspace.

        Args:
            width (int): The width of the module.
            height (int): The height of the module.
        """
        self._workspace = Workspace()
        self._logger = CustomLogger()
        self._config = Config()
        self._operation_control = OperationControl()
        self.width = width
        self._user_vars_width = int(self.width * 0.6)
        self._management_width = int(self.width * 0.20)
        self.height = height
        self.unique_id = str(uuid.uuid4())
        self.collection_list_id = f"collection_list_{self.unique_id}"
        self._collection_list = dict()

    async def initialize(self) -> None:
        """Initializes resources and sets up the GUI."""
        self.initialize_resources()
        await self.setup_workspace_pane()

    def initialize_resources(self) -> None:
        """Initializes necessary resources and logs the event."""
        pass

    async def setup_workspace_pane(self) -> None:
        """Sets up the workspace pane asynchronously."""
        with dpg.group(tag="workspace_pane_group", horizontal=True, parent="workspace_group"):
            with dpg.child_window(tag="workspace_management_pane", width=self._management_width, border=True,
                                  parent="workspace_pane_group"):
                dpg.add_text("Workspace Details")
                dpg.add_separator()
                dpg.add_text("Workspace Name:")
                dpg.add_input_text(tag="workspace_name_input", default_value=self._config.WORKSPACE_NAME, enabled=True,
                                   width=-1)
                dpg.add_button(label="Save Workspace", callback=lambda: asyncio.create_task(self.save_workspace()))
                dpg.add_button(label="Load Workspace", callback=lambda: asyncio.create_task(self.load_workspace()))
                dpg.add_separator()

    async def save_workspace(self) -> None:
        """Saves the current workspace."""
        try:
            await self._workspace.save_current_workspace()
            self._logger.info("Workspace saved successfully")
        except Exception as e:
            self._logger.error(Exception(f"Failed to save current workspace: {e}", self))

    async def load_workspace(self) -> None:
        """Loads a workspace."""
        try:
            workspace_path = os.path.normpath(dpg.get_value("workspace_name_input"))
            if not os.path.exists(workspace_path):
                path_attempt = os.path.normpath(os.path.join(self._config.BASE_DIR, workspace_path))
                if os.path.exists(path_attempt):
                    workspace_path = os.path.normpath(os.path.join(self._config.BASE_DIR, workspace_path,
                                                                   'config.json'))
            await self._workspace.load_workspace(workspace_path)
            self._logger.info("Workspace loaded successfully")
        except Exception as e:
            self._logger.error(Exception(f"Failed to load workspace: {e}", self))

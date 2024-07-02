import asyncio
import os
import dearpygui.dearpygui as dpg

from research_analytics_suite.gui.GUIBase import GUIBase
from research_analytics_suite.data_engine.Workspace import Workspace


class WorkspaceModule(GUIBase):
    """A class to manage the GUI representation of the Workspace."""

    def __init__(self, width: int, height: int, parent):
        """
        Initializes the WorkspaceModule with the given workspace.

        Args:
            width (int): The width of the module.
            height (int): The height of the module.
        """
        super().__init__(width, height, parent)
        self._workspace = Workspace()

        self._user_vars_width = int(self.width * 0.6)
        self._management_width = int(self.width * 0.20)

    async def initialize_gui(self) -> None:
        """Initializes resources and sets up the GUI."""
        pass

    async def _update_async(self) -> None:
        pass

    def draw(self) -> None:
        """Sets up the workspace pane."""
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

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        pass

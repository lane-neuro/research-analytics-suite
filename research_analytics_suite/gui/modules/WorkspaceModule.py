import asyncio
import os
import uuid
from typing import Optional, Any

import dearpygui.dearpygui as dpg

from research_analytics_suite.data_engine.utils.Config import Config
from research_analytics_suite.data_engine.Workspace import Workspace
from research_analytics_suite.operation_manager.control.OperationControl import OperationControl
from research_analytics_suite.operation_manager.operations.core.BaseOperation import BaseOperation
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
        self.update_operation = None
        self.unique_id = str(uuid.uuid4())
        self.collection_list_id = f"collection_list_{self.unique_id}"
        self._collection_list = dict()
        self.add_var_dialog_id = None

    async def initialize(self) -> None:
        """Initializes resources and sets up the GUI."""
        self.initialize_resources()
        await self.setup_workspace_pane()
        self.update_operation = await self.add_update_operation()

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
                dpg.add_button(label="Save Workspace", callback=lambda: asyncio.create_task(self.save_workspace()))
                dpg.add_button(label="Load Workspace", callback=lambda: asyncio.create_task(self.load_workspace()))
                dpg.add_separator()
                dpg.add_text("Workspace Name:")
                dpg.add_input_text(tag="workspace_name_input", default_value=self._config.WORKSPACE_NAME, enabled=False)
                dpg.add_separator()

                dpg.add_text("Save and Restore")
                dpg.add_separator()
                dpg.add_button(label="Save User Variables",
                               callback=lambda: asyncio.create_task(self.save_memory_collections()))
                dpg.add_button(label="Restore User Variables",
                               callback=lambda: asyncio.create_task(self.restore_memory_collections()))
                dpg.add_separator()
                dpg.add_text("Filename:")
                dpg.add_input_text(tag="save_path_input", default_value=os.path.join('user_variables.db'), width=-1)

            with dpg.child_window(label="Memory Collections",
                                  tag="memory_collections_pane",
                                  width=self._user_vars_width,
                                  border=True, parent="workspace_pane_group"):
                dpg.add_button(label="Add User Variable", callback=self.open_add_var_dialog)
                dpg.add_group(tag=self.collection_list_id)  # Create the group for memory collections list

    async def update_collections_list(self):
        """Updates the collection dropdown list and the GUI display of variables."""
        collections = await self._workspace.list_memory_collections()
        collection_items = []
        for collection_id, collection in collections.items():
            if collection.name.startswith('sys_') or collection.name.startswith('gui_'):
                continue
            collection_items.append(f"{collection.display_name}")
            self._collection_list[collection_id] = f"{collection.display_name}"
            await self.display_collection_in_gui(collection_id, collection)

        if dpg.does_item_exist("collection_id_input"):
            dpg.configure_item("collection_id_input", items=collection_items)

    async def display_collection_in_gui(self, collection_id, collection):
        """Displays or updates a collection and its variables in the GUI."""
        if collection.name.startswith('sys_') or collection.name.startswith('gui_'):
            return

        collection_group_tag = f"collection_group_{collection_id}"
        if not dpg.does_item_exist(collection_group_tag):
            with dpg.group(tag=collection_group_tag, parent=self.collection_list_id):
                dpg.add_text(f"{collection.display_name}", parent=collection_group_tag)
        else:
            dpg.configure_item(collection_group_tag, show=True)

        await self.update_slots_in_gui(collection_id, collection)

    async def update_slots_in_gui(self, collection_id, collection):
        """Updates the slots and their variables in the GUI."""
        if collection.list_slots():
            for slot in collection.list_slots():
                await self.display_slot_in_gui(collection_id, slot)

    async def display_slot_in_gui(self, collection_id, slot):
        """Displays or updates a memory slot and its variables in the GUI."""
        slot_group_tag = f"slot_group_{collection_id}_{slot.memory_id}"
        if not dpg.does_item_exist(slot_group_tag):
            with dpg.group(tag=slot_group_tag, parent=f"collection_group_{collection_id}", horizontal=True):
                dpg.add_text(f"Slot: {slot.name} (ID: {slot.memory_id})", parent=slot_group_tag)
        await self.update_variables_in_gui(collection_id, slot)

    async def update_variables_in_gui(self, collection_id, slot):
        """Updates the variables in a memory slot in the GUI."""
        slot_group_tag = f"slot_group_{collection_id}_{slot.memory_id}"
        for key, value in slot.data:
            var_tag = f"var_{collection_id}_{slot.memory_id}_{key}"
            if not dpg.does_item_exist(var_tag):
                dpg.add_text(f"{key}: {value}", tag=var_tag, parent=slot_group_tag)
            else:
                dpg.set_value(var_tag, f"{key}: {value}")

    async def add_update_operation(self) -> Optional[Any]:
        """Adds an update operation to refresh the GUI."""
        try:
            operation = await self._operation_control.operation_manager.add_operation_with_parameters(
                operation_type=BaseOperation, name="gui_WorkspaceUpdateTask",
                action=self.update_collections_loop, persistent=True, concurrent=True)
            operation.is_ready = True
            return operation
        except Exception as e:
            self._logger.error(e, self)
        return None

    async def update_collections_loop(self) -> None:
        """Periodically updates the user variables list in the GUI."""
        while True:
            await self.update_collections_list()
            await asyncio.sleep(0.05)

    async def add_variable_to_gui(self, collection_id, slot_id, key, value) -> None:
        """Adds a user variable to the GUI."""
        var_tag = f"var_{collection_id}_{slot_id}_{key}"
        slot_group_tag = f"slot_group_{collection_id}_{slot_id}"
        if not dpg.does_item_exist(var_tag):
            dpg.add_text(f"{key}: {value}", tag=var_tag, parent=slot_group_tag)
        else:
            dpg.set_value(var_tag, f"{key}: {value}")

    async def remove_memory_slot_from_gui(self, collection_id, slot_id=None) -> None:
        """Removes a memory slot from the GUI."""
        slot_group_tag = f"slot_group_{collection_id}_{slot_id}"
        if dpg.does_item_exist(slot_group_tag):
            dpg.delete_item(slot_group_tag)

    async def add_variable(self, name, value, collection_id: str, memory_slot_id: Optional[str] = None) -> None:
        """Adds a user variable."""
        try:
            await self._workspace.add_variable_to_collection(collection_id=collection_id, name=name, value=value,
                                                             memory_slot_id=memory_slot_id)
        except Exception as e:
            self._logger.error(Exception(f"Failed to add variable '{name}': {e}", self))

    async def remove_variable(self, name, collection_id, memory_slot_id: Optional[str] = None) -> None:
        """Removes a user variable."""
        try:
            await self._workspace.remove_variable_from_collection(collection_id, name, memory_slot_id)
        except Exception as e:
            self._logger.error(Exception(f"Failed to remove variable '{name}': {e}", self))

    async def save_memory_collections(self) -> None:
        """Backups the current memory collections to disk."""
        try:
            save_path = os.path.join(self._config.BASE_DIR, self._config.WORKSPACE_NAME,
                                     dpg.get_value("save_path_input"))
            await self._workspace.save_memory_manager(save_path)
            self._logger.debug(f"User variables saved to {save_path}")
        except Exception as e:
            self._logger.error(Exception(f"Failed to save user variables: {e}", self))

    async def restore_memory_collections(self) -> None:
        """Restores a memory collections file from disk."""
        try:
            restore_path = os.path.join(self._config.BASE_DIR, self._config.WORKSPACE_NAME,
                                        dpg.get_value("save_path_input"))
            await self._workspace.restore_memory_manager(restore_path)
            self._logger.debug(f"Memory restored from {restore_path}")
        except Exception as e:
            self._logger.error(Exception(f"Failed to restore memory bank: {e}", self))

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
            workspace_path = dpg.get_value("workspace_path_input")
            await self._workspace.load_workspace(workspace_path)
            self._logger.info("Workspace loaded successfully")
        except Exception as e:
            self._logger.error(Exception(f"Failed to load workspace: {e}", self))

    async def open_add_var_dialog(self) -> None:
        """Opens a dialog to add a user variable."""
        if dpg.does_item_exist(self.add_var_dialog_id):
            dpg.delete_item(self.add_var_dialog_id)

        self.add_var_dialog_id = dpg.generate_uuid()
        with dpg.window(label="Add User Variable", modal=True, tag=self.add_var_dialog_id):
            dpg.add_input_text(label="Variable Name", tag="var_name_input")
            dpg.add_input_text(label="Variable Value", tag="var_value_input")
            dpg.add_combo(label="Collection ID", tag="collection_id_input", items=[])
            dpg.add_input_text(label="Memory Slot ID (Optional)", tag="memory_slot_id_input")
            dpg.add_button(label="Add", callback=lambda: asyncio.create_task(self.add_user_variable_from_dialog()))
            dpg.add_button(label="Cancel", callback=lambda: dpg.hide_item(self.add_var_dialog_id))

    async def add_user_variable_from_dialog(self) -> None:
        """Adds a user variable from the dialog inputs."""
        try:
            name = dpg.get_value("var_name_input")
            value = dpg.get_value("var_value_input")
            # get the correct collection_id from _collection_list, based on the selected item in the combo
            collection_id = dpg.get_value("collection_id_input")

            for key, val in self._collection_list.items():
                if val == collection_id:
                    collection_id = key

            memory_slot_id = dpg.get_value("memory_slot_id_input")
            if not memory_slot_id:
                memory_slot_id = None
            await self.add_variable(name=name, value=value, collection_id=collection_id,
                                    memory_slot_id=memory_slot_id)
            dpg.hide_item(self.add_var_dialog_id)
        except Exception as e:
            self._logger.error(Exception(f"Error adding user variable: {e}", self))

"""
CollectionViewDialog.py

This module defines the CollectionViewDialog class, which is responsible for managing the main memory management window
and its components.
"""
import asyncio
import os
from typing import Optional, Any

import dearpygui.dearpygui as dpg
from research_analytics_suite.data_engine.memory.MemorySlotCollection import MemorySlotCollection
from research_analytics_suite.operation_manager import BaseOperation
from research_analytics_suite.utils import CustomLogger


class CollectionViewDialog:
    """A class to manage the main GUI window and its components."""

    def __init__(self, width: int, height: int, parent=None):
        """Initializes the CollectionViewDialog."""

        from research_analytics_suite.operation_manager import OperationControl
        self.operation_control = OperationControl()

        self._logger = CustomLogger()

        from research_analytics_suite.data_engine import MemoryManager
        self._memory_manager = MemoryManager()

        from research_analytics_suite.data_engine import Workspace
        self._workspace = Workspace()

        from research_analytics_suite.data_engine.utils.Config import Config
        self._config = Config()

        self.collections = []
        self.search_bar = None
        self.notification_area = None
        self.collection_list = None
        self.collection_groups = {}
        self.advanced_slot_view = None
        self.update_operation = None
        self.add_var_dialog_id = None

        self.parent = parent
        self.width = width
        self.height = height

    async def initialize_dialog(self) -> None:
        """Initializes the user interface."""
        with dpg.child_window(label="Memory Collections", tag="collection_view_dialog",
                              parent=self.parent, width=self.width, height=self.height, border=True):
            self.search_bar = dpg.add_input_text(label="Search", callback=self.search)
            dpg.add_button(label="Add User Variable", callback=self.open_add_var_dialog)

            dpg.add_text("Save and Restore")
            dpg.add_separator()
            dpg.add_button(label="Save User Variables",
                           callback=lambda: asyncio.create_task(self.save_memory_collections()))
            dpg.add_button(label="Restore User Variables",
                           callback=lambda: asyncio.create_task(self.restore_memory_collections()))
            dpg.add_separator()
            dpg.add_text("Filename:")
            dpg.add_input_text(tag="save_path_input", default_value=os.path.join('user_variables.db'), width=-1)

            self.notification_area = dpg.add_text("Notifications will appear here.")
            self.advanced_slot_view = None
            dpg.add_child_window(tag="data_collection_tools_group", border=True, width=-1, height=-1)

        self.update_operation = await self.add_update_operation()

    async def draw_collections(self):
        if dpg.does_item_exist("collection_group"):
            dpg.delete_item("collection_group")

        with dpg.group(parent="data_collection_tools_group", tag="collection_group", width=-1, height=-1):
            """Draws the collection summary view elements."""
            if self.collection_list is None:
                return

            for collection in self.collection_list:
                collection = await self._memory_manager.get_collection(collection)
                if collection.name.startswith("gui_") or collection.name.startswith("sys_"):
                    continue
                collection_tag = f"collection_group_{collection}"
                self.collection_groups[collection] = collection_tag

                with dpg.group(tag=collection_tag, horizontal=True):
                    dpg.add_text(f"Collection: {collection.name}", parent=collection_tag)
                    if collection.list_slots():
                        for slot in collection.list_slots():
                            from research_analytics_suite.gui import SlotPreview
                            slot_preview = SlotPreview(parent=collection_tag, slot=slot, width=200, height=100)
                            slot_preview.draw()

    async def add_update_operation(self) -> Optional[Any]:
        try:
            operation = await self.operation_control.operation_manager.add_operation_with_parameters(
                operation_type=BaseOperation, name="gui_MainCollectionUpdateTask",
                action=self.update_collections, persistent=True, concurrent=True)
            operation.is_ready = True
            return operation
        except Exception as e:
            self._logger.error(e, self)
        return None

    def search(self, sender, data):
        """Callback function for search bar."""
        search_query = dpg.get_value(self.search_bar)
        # Logic for searching collections and slots based on the query

    def add_collection(self, collection: MemorySlotCollection):
        """Adds a new collection to the primary view."""
        self.collections.append(collection)
        self.add_collection(collection)

    def remove_collection(self, collection_id: str):
        """Removes a collection from the primary view."""
        self.collections = [c for c in self.collections if c.collection_id != collection_id]
        self.remove_collection(collection_id)

    def show_advanced_slot_view(self, slot):
        """Displays the advanced slot view for a given slot."""
        _slot_name = slot.name
        if dpg.does_item_exist(f"advanced_slot_window_{_slot_name}"):
            dpg.delete_item(f"advanced_slot_window_{_slot_name}")

        with dpg.window(label=f"Advanced View - {_slot_name}",
                        tag=f"advanced_slot_window_{_slot_name}",
                        width=500, height=500):
            from research_analytics_suite.gui import AdvancedSlotView
            self.advanced_slot_view = AdvancedSlotView(parent="advanced_slot_group", slot=slot)

    async def update_collections(self):
        """Updates the collection dropdown list and the GUI display of variables."""
        while not dpg.does_item_exist("data_collection_tools_group"):
            await asyncio.sleep(0.1)

        while True:
            collections = await self._workspace.list_memory_collections()
            collection_items = []
            for collection_id, collection in collections.items():
                if collection.name.startswith('sys_') or collection.name.startswith('gui_'):
                    continue
                collection_items.append(f"{collection.display_name}")
                self.collection_groups[collection_id] = f"{collection.display_name}"
                await self.display_collection_in_gui(collection_id, collection)

            if dpg.does_item_exist("collection_id_input"):
                dpg.configure_item("collection_id_input", items=collection_items)

            await asyncio.sleep(0.05)

    async def display_collection_in_gui(self, collection_id, collection):
        """Displays or updates a collection and its variables in the GUI."""
        if collection.name.startswith('sys_') or collection.name.startswith('gui_'):
            return

        collection_group_tag = f"collection_group_{collection_id}"
        if not dpg.does_item_exist(collection_group_tag):
            with dpg.group(tag=collection_group_tag, parent="data_collection_tools_group", horizontal=True):
                dpg.add_text(f"Collection: {collection.display_name}")
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

    def show_data_import(self, sender, app_data, user_data):
        self._logger.info("Data Import clicked")

    def show_surveys_forms(self, sender, app_data, user_data):
        self._logger.info("Surveys/Forms clicked")

    def show_sensor_integration(self, sender, app_data, user_data):
        self._logger.info("Sensor Integration clicked")

    def show_manual_entry(self, sender, app_data, user_data):
        self._logger.info("Manual Entry clicked")

    def show_data_quality_checks(self, sender, app_data, user_data):
        self._logger.info("Data Quality Checks clicked")

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

    async def open_add_var_dialog(self) -> None:
        """Opens a dialog to add a user variable."""
        if dpg.does_item_exist(self.add_var_dialog_id):
            dpg.delete_item(self.add_var_dialog_id)

        self.add_var_dialog_id = dpg.generate_uuid()
        with dpg.window(label="Add Variable to Collection", modal=True, tag=self.add_var_dialog_id):
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
            selected_collection_display_name = dpg.get_value("collection_id_input")

            collection_id = None
            print(self.collection_groups)
            for _id, collection in self.collection_groups.items():
                if collection == selected_collection_display_name:
                    collection_id = _id
                    break

            memory_slot_id = dpg.get_value("memory_slot_id_input")
            if not memory_slot_id:
                memory_slot_id = None

            if collection_id:
                await self.add_variable(name=name, value=value, collection_id=collection_id,
                                        memory_slot_id=memory_slot_id)
                dpg.hide_item(self.add_var_dialog_id)
            else:
                self._logger.error(Exception(f"Collection ID not found"), self)

        except Exception as e:
            self._logger.error(Exception(f"Error adding user variable: {e}", self))

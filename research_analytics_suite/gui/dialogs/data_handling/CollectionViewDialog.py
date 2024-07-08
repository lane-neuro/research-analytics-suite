import asyncio
import os
import sys
from typing import Optional

import dearpygui.dearpygui as dpg
from research_analytics_suite.data_engine.memory.MemorySlotCollection import MemorySlotCollection
from research_analytics_suite.gui.GUIBase import GUIBase
from research_analytics_suite.operation_manager import BaseOperation


class CollectionViewDialog(GUIBase):
    """A class to manage the main GUI window and its components."""

    def __init__(self, width: int, height: int, parent):
        """Initializes the CollectionViewDialog."""
        super().__init__(width, height, parent)

        from research_analytics_suite.data_engine import MemoryManager
        self._memory_manager = MemoryManager()

        from research_analytics_suite.data_engine import Workspace
        self._workspace = Workspace()

        self.collections = []
        self.search_bar = None
        self.notification_area = None
        self.collection_list = None
        self.collection_groups = {}
        self.advanced_slot_view = None
        self.add_var_dialog_id = None

    async def initialize_gui(self) -> None:
        """Initializes the user interface."""
        try:
            self._update_operation = await self._operation_control.operation_manager.add_operation_with_parameters(
                operation_type=BaseOperation, name="gui_MainCollectionUpdateTask",
                action=self._update_async, is_loop=True, parallel=True)
            self._update_operation.is_ready = True
        except Exception as e:
            self._logger.error(e, self)

    def draw(self) -> None:
        with dpg.child_window(tag="collection_view_dialog",
                              parent=self._parent, width=-1, height=125, border=True):
            from research_analytics_suite.gui import left_aligned_input_field
            left_aligned_input_field(label="Search", tag="search_input", parent="collection_view_dialog",
                                     callback=self.search, value="")
            dpg.add_separator()

            with dpg.group(horizontal=True):
                with dpg.group(horizontal=False, width=200):
                    dpg.add_text("Save and Restore")
                    dpg.add_separator()
                    dpg.add_button(label="Save Memory Collections",
                                   callback=lambda: asyncio.create_task(self.save_memory_collections()))
                    dpg.add_button(label="Restore Memory Collections",
                                   callback=lambda: asyncio.create_task(self.restore_memory_collections()))
                with dpg.group(horizontal=False, width=200):
                    dpg.add_text("Filename")
                    dpg.add_separator()
                    dpg.add_input_text(tag="save_path_input", default_value=os.path.join('user_variables.db'), width=-1)
                with dpg.group(horizontal=False, width=-1):
                    self.notification_area = dpg.add_text("Notifications: [in the future]")
                    dpg.add_separator()

        dpg.add_child_window(label="Memory Collections", parent=self._parent, width=-1, height=-1,
                             border=True, tag="memory_collections_window")
        dpg.add_button(label="Add Variable", parent="memory_collections_window",
                       callback=lambda: asyncio.create_task(self.open_add_var_dialog()))
        dpg.add_button(label="Data Import", parent="memory_collections_window",
                       callback=self.show_data_import)
        dpg.add_group(tag="data_collection_tools_group", parent="memory_collections_window", width=-1, height=-1,
                      horizontal=True)

    async def _update_async(self) -> None:
        """Updates the collection dropdown list and the GUI display of variables."""
        while not dpg.does_item_exist("data_collection_tools_group"):
            await asyncio.sleep(0.001)

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

            await asyncio.sleep(0.005)

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        """Resizes the GUI."""
        self.width = new_width
        self.height = new_height
        dpg.set_item_width("collection_view_dialog", new_width)
        dpg.set_item_height("collection_view_dialog", new_height)

    async def draw_collections(self):
        if dpg.does_item_exist("collection_group"):
            dpg.delete_item("collection_group")

        with dpg.group(parent="data_collection_tools_group", tag="collection_group",
                       width=-1, height=-1, horizontal=True):
            """Draws the collection summary view elements."""
            if self.collection_list is None:
                return

            for collection in self.collection_list:
                collection = self._memory_manager.get_collection(collection)
                if collection.name.startswith("gui_") or collection.name.startswith("sys_"):
                    continue
                collection_tag = f"collection_group_{collection}"
                self.collection_groups[collection] = collection_tag

                with dpg.group(tag=collection_tag, horizontal=False):
                    dpg.add_text(collection.name, parent=collection_tag)
                    if collection.list_slots():
                        for slot in collection.list_slots():
                            from research_analytics_suite.gui import MemorySlotPreview
                            slot_preview = MemorySlotPreview(parent=collection_tag, slot=slot, width=200, height=100)
                            slot_preview.draw()

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

    async def display_collection_in_gui(self, collection_id, collection):
        """Displays or updates a collection and its variables in the GUI."""
        if collection.name.startswith('sys_') or collection.name.startswith('gui_'):
            return

        collection_group_tag = f"collection_group_{collection_id}"
        if not dpg.does_item_exist(collection_group_tag):
            with dpg.group(tag=collection_group_tag, parent="data_collection_tools_group", horizontal=False):
                dpg.add_text(f"{collection.display_name}", tag=f"collection_{collection_id}_name")
        else:
            dpg.configure_item(collection_group_tag, show=True)

        await self.update_slots_in_gui(collection_id, collection)

    async def update_slots_in_gui(self, collection_id, collection):
        """Updates the slots and their variables in the GUI."""
        if collection.list_slots():
            for slot in collection.list_slots():
                if slot is not None:
                    await self.display_slot_in_gui(collection_id, slot)

    async def display_slot_in_gui(self, collection_id, slot):
        """Displays or updates a memory slot and its variables in the GUI."""
        slot_group_tag = f"slot_group_{collection_id}_{slot.memory_id}"
        if not dpg.does_item_exist(slot_group_tag):
            with dpg.group(tag=slot_group_tag, parent=f"collection_group_{collection_id}", horizontal=False):
                dpg.add_text(f"Slot: {slot.name}", parent=slot_group_tag)
        await self.update_variables_in_gui(collection_id, slot)

    async def update_variables_in_gui(self, collection_id, slot):
        """Updates the variables in a memory slot in the GUI."""
        slot_group_tag = f"slot_group_{collection_id}_{slot.memory_id}"
        for key, (data_type, value) in slot.data.items():
            var_tag = f"var_{collection_id}_{slot.memory_id}_{key}"
            if not dpg.does_item_exist(var_tag):
                dpg.add_text(f"{key}: {value} ({data_type.__name__})", tag=var_tag, parent=slot_group_tag)
            else:
                dpg.set_value(var_tag, f"{key}: {value} ({data_type.__name__})")

    async def remove_memory_slot_from_gui(self, collection_id, slot_id=None) -> None:
        """Removes a memory slot from the GUI."""
        slot_group_tag = f"slot_group_{collection_id}_{slot_id}"
        if dpg.does_item_exist(slot_group_tag):
            dpg.delete_item(slot_group_tag)

    async def add_variable(self, name, value, data_type, collection_id: str,
                           memory_slot_id: Optional[str] = None) -> None:
        """Adds a user variable."""
        try:
            await self._workspace.add_variable_to_collection(collection_id=collection_id, name=name, value=value,
                                                             data_type=data_type, memory_slot_id=memory_slot_id)
        except Exception as e:
            self._logger.error(Exception(f"Failed to add variable '{name}': {e}", self))

    async def remove_variable(self, name, collection_id, memory_slot_id: Optional[str] = None) -> None:
        """Removes a user variable."""
        try:
            await self._workspace.remove_variable_from_collection(collection_id, name, memory_slot_id)
        except Exception as e:
            self._logger.error(Exception(f"Failed to remove variable '{name}': {e}", self))

    def show_data_import(self, sender, app_data, user_data):
        if dpg.does_item_exist("selected_file"):
            dpg.delete_item("selected_file")

        with dpg.file_dialog(show=True,
                             default_path=f"{self._config.BASE_DIR}/{self._config.WORKSPACE_NAME}/"
                                          f"{self._config.DATA_DIR}",
                             callback=self._import_data,
                             tag="selected_file",
                             width=500, height=500, modal=True):
            dpg.add_file_extension(".json", color=(255, 255, 255, 255))
            dpg.add_file_extension(".csv", color=(255, 255, 255, 255))
            dpg.add_file_extension(".xlsx", color=(255, 255, 255, 255))
            dpg.add_file_extension(".txt", color=(255, 255, 255, 255))
            dpg.add_file_extension(".tsv", color=(255, 255, 255, 255))
            dpg.add_file_extension(".xml", color=(255, 255, 255, 255))
            dpg.add_file_extension(".hd5", color=(255, 255, 255, 255))

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
            self._logger.debug(f"Memory collections saved to {save_path}")
        except Exception as e:
            self._logger.error(Exception(f"Failed to save memory collections: {e}", self))

    async def restore_memory_collections(self) -> None:
        """Restores a memory collections file from disk."""
        try:
            restore_path = os.path.join(self._config.BASE_DIR, self._config.WORKSPACE_NAME,
                                        dpg.get_value("save_path_input"))
            await self._workspace.restore_memory_manager(restore_path)
            self._logger.debug(f"Memory collections restored from {restore_path}")
        except Exception as e:
            self._logger.error(Exception(f"Failed to restore memory collections: {e}", self))

    async def update_slot_combobox(self):
        """Updates the slot combobox in the GUI."""
        if dpg.does_item_exist("memory_slot_id_input"):
            slot_items = []
            slots = self._memory_manager.get_collection_by_display_name(
                dpg.get_value("collection_id_input"))
            if slots.list_slots():
                for slot in slots.list_slots():
                    slot_items.append(f"{slot.name}")

            dpg.configure_item("memory_slot_id_input", items=slot_items,
                               default_value=slot_items[0] if slot_items else "")

    async def open_add_var_dialog(self) -> None:
        """Opens a dialog to add a user variable."""
        if dpg.does_item_exist(self.add_var_dialog_id):
            dpg.delete_item(self.add_var_dialog_id)

        self.add_var_dialog_id = dpg.generate_uuid()
        with dpg.window(label="Add Variable to Collection", modal=True, tag=self.add_var_dialog_id):
            dpg.add_input_text(label="Variable Name", tag="var_name_input")
            dpg.add_combo(label="Data Type", tag="var_data_type_input", items=["int", "float", "str", "list", "dict"],
                          callback=self.update_var_value_input)
            dpg.add_input_text(label="Data Value", tag="var_value_input")
            dpg.add_combo(label="Collection", tag="collection_id_input", items=[],
                          callback=self.update_slot_combobox)
            dpg.add_combo(label="Memory Slot", tag="memory_slot_id_input", items=[])
            dpg.add_button(label="Add", callback=lambda: asyncio.create_task(self.add_user_variable_from_dialog()))
            dpg.add_button(label="Cancel", callback=lambda: dpg.hide_item(self.add_var_dialog_id))

    def update_var_value_input(self, sender, app_data):
        """Updates the variable value input field based on the selected data type."""
        data_type = dpg.get_value("var_data_type_input")
        var_value = dpg.get_value("var_value_input")

        # Adjust input field based on the selected data type
        if data_type in ["int", "float", "str"]:
            dpg.configure_item("var_value_input", default_value="")
        elif data_type == "list":
            dpg.configure_item("var_value_input", default_value="[]")
        elif data_type == "dict":
            dpg.configure_item("var_value_input", default_value="{}")

        dpg.set_value("var_value_input", var_value)

    async def add_user_variable_from_dialog(self) -> None:
        """Adds a user variable from the dialog inputs."""
        try:
            name = dpg.get_value("var_name_input")
            value = dpg.get_value("var_value_input")
            data_type_str = dpg.get_value("var_data_type_input")
            selected_collection_display_name = dpg.get_value("collection_id_input")

            # Map string representation of data type to actual type
            data_type_map = {
                "int": int,
                "float": float,
                "str": str,
                "list": list,
                "dict": dict
            }
            data_type = data_type_map.get(data_type_str, str)

            # Convert value to the appropriate data type
            if data_type == int:
                value = int(value)
            elif data_type == float:
                value = float(value)
            elif data_type == list:
                value = eval(value)
            elif data_type == dict:
                value = eval(value)

            collection_id = None
            for _id, collection in self.collection_groups.items():
                if collection == selected_collection_display_name:
                    collection_id = _id
                    break

            memory_slot_id = dpg.get_value("memory_slot_id_input")
            if not memory_slot_id:
                memory_slot_id = None

            if collection_id:
                await self.add_variable(name=name, value=value, data_type=data_type, collection_id=collection_id,
                                        memory_slot_id=memory_slot_id)
                dpg.hide_item(self.add_var_dialog_id)
            else:
                self._logger.error(Exception(f"Collection ID not found"), self)

        except Exception as e:
            self._logger.error(Exception(f"Error adding user variable: {e}", self))

    def _import_data(self, sender, app_data, user_data):
        """
        Imports data from the selected file into the data engine.

        Args:
            sender: Sender of the import data command.
            app_data: Application data.
            user_data: User data.
        """
        _selected_files = app_data['selections'].values()
        if not _selected_files:
            return

        for file in _selected_files:
            file_path = file
            data = self._workspace.get_default_data_engine().load_data(file_path)
            collection = self._memory_manager.get_default_collection_id()
            collection = self._memory_manager.get_collection(collection)
            collection.new_slot_with_data(data)

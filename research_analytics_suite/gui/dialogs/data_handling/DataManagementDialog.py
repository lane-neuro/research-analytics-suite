import asyncio
import os
import dearpygui.dearpygui as dpg
from research_analytics_suite.gui.GUIBase import GUIBase
from research_analytics_suite.operation_manager.operations.system.UpdateMonitor import UpdateMonitor


class DataManagementDialog(GUIBase):
    """ A class to manage the data management dialog for the Research Analytics Suite.
    """

    def __init__(self, width: int, height: int, parent):
        """Initializes the DataManagementDialog."""
        super().__init__(width, height, parent)

        from research_analytics_suite.data_engine.memory.MemoryManager import MemoryManager
        self._memory_manager = MemoryManager()

        from research_analytics_suite.data_engine import Workspace
        self._workspace = Workspace()

        self.memory_slots = set()
        self.search_bar = None
        self.notification_area = None
        self.advanced_slot_view = None
        self.add_var_dialog_id = None

    async def initialize_gui(self) -> None:
        """Initializes the user interface."""
        try:
            self._update_operation = await self._operation_control.operation_manager.create_operation(
                operation_type=UpdateMonitor, name="gui_DataManUpdate", action=self._update_async)
            self._update_operation.is_ready = True
        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    def draw(self) -> None:
        with dpg.child_window(tag="data_man_dialog",
                              parent=self._parent, width=-1, height=125, border=True):
            from research_analytics_suite.gui import left_aligned_input_field
            left_aligned_input_field(label="Search", tag="search_input", parent="data_man_dialog",
                                     callback=self.search, value="")
            dpg.add_separator()

            with dpg.group(horizontal=True):
                with dpg.group(horizontal=False, width=200):
                    dpg.add_text("Save and Restore")
                    dpg.add_separator()
                    dpg.add_button(label="Save Memory Slots",
                                   callback=lambda: asyncio.create_task(self.save_memory_slots()))
                    dpg.add_button(label="Restore Memory Slots",
                                   callback=lambda: asyncio.create_task(self.restore_memory_slots()))
                with dpg.group(horizontal=False, width=200):
                    dpg.add_text("Filename")
                    dpg.add_separator()
                    dpg.add_input_text(tag="save_path_input", default_value=os.path.join('memory_manager.db'), width=-1)
                with dpg.group(horizontal=False, width=-1):
                    self.notification_area = dpg.add_text("Notifications: [in the future]")
                    dpg.add_separator()

        dpg.add_child_window(label="Memory Slots", parent=self._parent, width=-1, height=-1,
                             border=True, tag="slots_window")
        dpg.add_button(label="Add Variable", parent="slots_window",
                       callback=lambda: asyncio.create_task(self.open_add_var_dialog()))
        dpg.add_button(label="Data Import", parent="slots_window",
                       callback=self.show_data_import)
        dpg.add_group(tag="management_tools_group", parent="slots_window", width=-1, height=-1,
                      horizontal=True)

    async def _update_async(self) -> None:
        """Updates the collection dropdown list and the GUI display of variables."""
        while not self._update_operation.is_running:
            await asyncio.sleep(.1)

        while True:
            await asyncio.sleep(.001)

            slots = self._memory_manager.list_slots()
            dpg.delete_item("management_tools_group")

            with dpg.group(tag="management_tools_group", parent="slots_window", width=-1, height=-1):
                for slot_info in slots:
                    dpg.add_text(f"Slot ID: {slot_info.memory_id}, Name: {slot_info.name}, Data: {slot_info.data}")

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        """Resizes the GUI."""
        self.width = new_width
        self.height = new_height
        dpg.set_item_width("data_man_dialog", new_width)
        dpg.set_item_height("data_man_dialog", new_height)

    def search(self, sender, data):
        """Callback function for search bar."""
        search_query = dpg.get_value("search_input")
        # Logic for searching memory_slots and slots based on the query

    def add_memory_slot(self, slot_id: str):
        """Adds a new collection to the primary view."""
        self.memory_slots.add(slot_id)

    def remove_memory_slot(self, slot_id: str):
        """Removes a collection from the primary view."""
        self.memory_slots = {c for c in self.memory_slots if c.memory_id != slot_id}

    async def add_variable(self, name, d_type, value) -> None:
        """Adds a user variable."""
        try:
            _slot_id = await self._memory_manager.create_slot(name=name, d_type=d_type, data=value)
            self.add_memory_slot(_slot_id)
        except Exception as e:
            self._logger.error(Exception(f"Failed to add variable '{name}': {e}", self))

    async def remove_variable(self, slot_id: str) -> None:
        """Removes a user variable."""
        try:
            await self._memory_manager.delete_slot(slot_id)
            self.remove_memory_slot(slot_id)
        except Exception as e:
            self._logger.error(Exception(f"Failed to remove variable '{slot_id}': {e}", self))

    def show_data_import(self, sender, app_data, user_data):
        if dpg.does_item_exist("selected_file"):
            dpg.delete_item("selected_file")

        with dpg.file_dialog(show=True,
                             default_path=f"{self._config.BASE_DIR}/{self._config.WORKSPACE_NAME}/"
                                          f"{self._config.DATA_DIR}",
                             callback=asyncio.create_task(self._import_data),
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

    async def save_memory_slots(self) -> None:
        """Backups the current memory collections to disk."""
        ...

    async def restore_memory_slots(self) -> None:
        """Restores a memory collections file from disk."""
        ...

    async def open_add_var_dialog(self) -> None:
        """Opens a dialog to add a user variable."""
        if dpg.does_item_exist(self.add_var_dialog_id):
            dpg.delete_item(self.add_var_dialog_id)

        self.add_var_dialog_id = dpg.generate_uuid()
        with dpg.window(label="Add Memory Slot", modal=True, tag=self.add_var_dialog_id):
            dpg.add_input_text(label="Variable Name", tag="var_name_input")
            dpg.add_combo(label="Data Type", tag="var_data_type_input",
                          items=["int", "float", "str", "list", "dict", "set"],
                          callback=self.update_var_value_input)
            dpg.add_input_text(label="Data Value", tag="var_value_input")
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
        elif data_type == "bool":
            dpg.configure_item("var_value_input", default_value="True")
        elif data_type == "type":
            dpg.configure_item("var_value_input", default_value="int")
        elif data_type == "set":
            dpg.configure_item("var_value_input", default_value="")

        dpg.set_value("var_value_input", var_value)

    async def add_user_variable_from_dialog(self) -> None:
        """Adds a user variable from the dialog inputs."""
        try:
            name = dpg.get_value("var_name_input")
            value = dpg.get_value("var_value_input")
            data_type_str = dpg.get_value("var_data_type_input")

            # Map string representation of data type to actual type
            data_type_map = {
                "int": int,
                "float": float,
                "str": str,
                "list": list,
                "dict": dict,
                "set": set,
                "bool": bool,
                "type": type
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
            elif data_type == str:
                value = str(value)
            elif data_type == bool:
                value = bool(value)
            elif data_type == type:
                value = type(value)
            elif data_type == set:
                value = set(value)

            await self.add_variable(name=name, d_type=data_type, value=value)
            dpg.hide_item(self.add_var_dialog_id)

        except Exception as e:
            self._logger.error(Exception(f"Error adding user variable: {e}", self))

    async def _import_data(self, sender, app_data, user_data):
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
            data, d_type = self._workspace.get_default_data_engine().load_data(file_path)
            if data:
                _name = os.path.basename(file_path)
                await self.add_variable(name=file_path, d_type=d_type, value=data)

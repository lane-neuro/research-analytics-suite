import dearpygui.dearpygui as dpg

from research_analytics_suite.gui.modules.PrimaryView import PrimaryView
from research_analytics_suite.utils import CustomLogger


class DataCollectionDialog:
    """A class to manage Data Collection tools and their GUI representation."""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.primary_view = None
        self._logger = CustomLogger()

    def draw(self, parent):
        with dpg.group(parent=parent, tag="data_collection_tools_group"):
            dpg.add_text("Data Collection Tools")

    async def show_memory_collections(self):
        with dpg.group(label="Memory Collections", tag="memory_collections_group",
                       parent="data_collection_tools_group", width=-1, height=-1):
            self.primary_view = PrimaryView(parent="memory_collections_group")
            await self.primary_view.initialize_dialog()

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

    def show_advanced_view(self, slot):
        """Displays the Advanced Slot View for a given slot."""
        from research_analytics_suite.gui import AdvancedSlotView
        advanced_view = AdvancedSlotView(parent="data_sources_window", slot=slot)
        advanced_view.draw()

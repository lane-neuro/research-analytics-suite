import dearpygui.dearpygui as dpg
from dearpygui_async import DearPyGuiAsync
from neurobehavioral_analytics_suite.data_engine.DataEngine import DataEngine
from neurobehavioral_analytics_suite.gui.ConsoleDialog import ConsoleDialog
from neurobehavioral_analytics_suite.operation_manager.OperationControl import OperationControl


class GuiLauncher:
    def __init__(self, data_engine: DataEngine, operation_control: OperationControl, logger):
        self.logger = logger
        self.operation_control = operation_control
        self.data_engine = data_engine
        self.resource_monitor = None
        self.console = None
        self.operation_window = None
        self.project_manager = None

        self.update_operations = []

        self.dpg_async = DearPyGuiAsync()

    async def setup_navigation_menu(self):
        with dpg.group(parent="left_pane"):
            dpg.add_button(label="Import Data", callback=lambda: self.switch_pane("import_data"))
            dpg.add_button(label="Analyze Data", callback=lambda: self.switch_pane("analyze_data"))
            dpg.add_button(label="Visualize Data", callback=lambda: self.switch_pane("visualize_data"))
            dpg.add_button(label="Manage Projects", callback=lambda: self.switch_pane("manage_projects"))
            dpg.add_button(label="Reports", callback=lambda: self.switch_pane("reports"))
            dpg.add_button(label="Settings", callback=lambda: self.switch_pane("settings"))

    def switch_pane(self, pane_name):
        # Hide all panes first
        for pane in ["import_data_pane", "analyze_data_pane", "visualize_data_pane", "manage_projects_pane",
                     "reports_pane", "settings_pane"]:
            dpg.configure_item(pane, show=False)

        # Show the selected pane
        dpg.configure_item(f"{pane_name}_pane", show=True)

    async def setup_data_analysis_pane(self):
        with dpg.group(parent="data_analysis_pane"):
            dpg.add_text("Data Analysis Tools")
            # Add more widgets for data analysis

    async def setup_visualization_pane(self):
        with dpg.group(parent="visualization_pane"):
            dpg.add_text("Data Visualization Tools")
            # Add more widgets for data visualization

    async def setup_console_log_viewer(self):
        with dpg.group(parent="bottom_pane"):
            dpg.add_text("Console/Log Output", tag="console_log_output")

        self.console = ConsoleDialog(self.operation_control.user_input_handler, self.operation_control, self.logger)
        await self.console.initialize()

    async def setup_panes(self):
        with dpg.child_window(tag="import_data_pane", parent="right_pane", show=True):
            dpg.add_text("Import Data Pane")

        with dpg.child_window(tag="analyze_data_pane", parent="right_pane", show=False):
            await self.setup_data_analysis_pane()

        with dpg.child_window(tag="visualize_data_pane", parent="right_pane", show=False):
            await self.setup_visualization_pane()

        with dpg.child_window(tag="manage_projects_pane", parent="right_pane", show=False):
            dpg.add_text("Manage Projects Pane")

        with dpg.child_window(tag="reports_pane", parent="right_pane", show=False):
            dpg.add_text("Reports Pane")

        with dpg.child_window(tag="settings_pane", parent="right_pane", show=False):
            dpg.add_text("Settings Pane")

    async def setup_main_window(self):
        dpg.create_context()

        with dpg.window(label="NBAS", tag="main_window"):
            with dpg.group(horizontal=True):
                with dpg.child_window(tag="left_pane", width=200):
                    await self.setup_navigation_menu()

                with dpg.child_window(tag="right_pane"):
                    await self.setup_panes()

            with dpg.child_window(tag="bottom_pane", height=200):
                await self.setup_console_log_viewer()

        dpg.create_viewport(title='NeuroBehavioral Analytics Suite', width=1280, height=720)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("main_window", True)
        dpg.start_dearpygui()
        dpg.destroy_context()

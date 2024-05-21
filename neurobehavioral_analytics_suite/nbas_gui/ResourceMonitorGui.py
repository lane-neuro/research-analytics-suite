# neurobehavioral_analytics_suite/nbas_gui/ResourceMonitorGui.py
import dearpygui.dearpygui as dpg
import asyncio
import psutil

from neurobehavioral_analytics_suite.operation_handler.OperationHandler import OperationHandler


class ResourceMonitorGui:
    SLEEP_DURATION = 0.05

    def __init__(self, operation_handler: OperationHandler):
        self.memory_line_series = None
        self.memory_x_axis = None
        self.memory_y_axis = None
        self.memory_history = None
        self.memory_text = None
        self.cpu_line_series = None
        self.cpu_y_axis = None
        self.cpu_x_axis = None
        self.cpu_history = None
        self.cpu_text = None

        self.operation_handler = operation_handler

        self.window = dpg.add_window(label="Resource Monitor")
        self.cpu_data = []
        self.memory_data = []

        # Create a container for each monitor
        self.cpu_container = dpg.add_child_window(parent=self.window)
        self.memory_container = dpg.add_child_window(parent=self.window)

        # Set up the CPU and memory monitors in their respective containers
        self.setup_cpu_monitor(self.cpu_container)
        self.setup_memory_monitor(self.memory_container)

        self.update_task = asyncio.create_task(self.update_resource_usage())

    def setup_cpu_monitor(self, parent):
        self.cpu_text = dpg.add_text("CPU Usage: 0%", parent=parent)
        self.cpu_history = dpg.add_plot(label="CPU Usage History (%)", parent=parent)
        self.cpu_x_axis = dpg.add_plot_axis(axis=0, label="Time", parent=self.cpu_history)
        self.cpu_y_axis = dpg.add_plot_axis(axis=1, label="CPU Usage", parent=self.cpu_history)
        dpg.set_axis_limits(self.cpu_y_axis, 0, 100)
        self.cpu_line_series = None

    def setup_memory_monitor(self, parent):
        self.memory_text = dpg.add_text("Memory Usage: 0%", parent=parent)
        self.memory_history = dpg.add_plot(label="Memory Usage History (%)", parent=parent)
        self.memory_x_axis = dpg.add_plot_axis(axis=0, label="Time", parent=self.memory_history)
        self.memory_y_axis = dpg.add_plot_axis(axis=1, label="Memory Usage", parent=self.memory_history)
        dpg.set_axis_limits(self.memory_y_axis, 0, 100)
        self.memory_line_series = None

    async def update_resource_usage(self):
        while True:
            self.update_cpu_usage()
            self.update_memory_usage()
            await asyncio.sleep(self.SLEEP_DURATION)

    def update_cpu_usage(self):
        cpu_usage = psutil.cpu_percent()
        self.cpu_data.append(cpu_usage)
        dpg.set_value(self.cpu_text, f"CPU Usage: {cpu_usage}%")
        self.update_line_series(self.cpu_data, self.cpu_x_axis, self.cpu_y_axis, self.cpu_line_series, "CPU Usage")

    def update_memory_usage(self):
        memory_usage = psutil.virtual_memory().percent
        self.memory_data.append(memory_usage)
        dpg.set_value(self.memory_text, f"Memory Usage: {memory_usage}%")
        self.update_line_series(self.memory_data, self.memory_x_axis, self.memory_y_axis, self.memory_line_series,
                                "Memory Usage")

    def update_line_series(self, data, x_axis, y_axis, line_series, label):
        if line_series:
            dpg.delete_item(line_series)
        x_data = list(range(len(data)))
        dpg.set_axis_limits(x_axis, 0, len(x_data) + 1)
        dpg.set_axis_limits(y_axis, min(data) - 5, max(data) + 5)
        line_series = dpg.add_line_series(x_data, data, label=label, parent=y_axis)

    def update_layout(self):
        # Configure the size and position of the containers
        dpg.configure_item(self.cpu_container, pos=(0, 0), width=dpg.get_item_width(self.window) // 2,
                           height=dpg.get_item_height(self.window))
        dpg.configure_item(self.memory_container, pos=(dpg.get_item_width(self.cpu_container), 0),
                           width=dpg.get_item_width(self.window) // 2, height=dpg.get_item_height(self.window))

        # Configure the size of the plots to match the size of their respective containers
        dpg.configure_item(self.cpu_history, width=dpg.get_item_width(self.cpu_container),
                           height=dpg.get_item_height(self.cpu_container))
        dpg.configure_item(self.memory_history, width=dpg.get_item_width(self.memory_container),
                           height=dpg.get_item_height(self.memory_container))
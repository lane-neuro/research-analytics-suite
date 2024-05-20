# neurobehavioral_analytics_suite/nbas_gui/ResourceMonitorGui.py
import dearpygui.dearpygui as dpg
import asyncio
import psutil

from neurobehavioral_analytics_suite.operation_handler.OperationHandler import OperationHandler


class ResourceMonitorGui:
    def __init__(self, operation_handler: OperationHandler):
        self.operation_handler = operation_handler
        self.window = dpg.add_window(label="Resource Monitor")
        self.cpu_text = dpg.add_text("CPU Usage: 0%", parent=self.window)
        self.memory_text = dpg.add_text("Memory Usage: 0%", parent=self.window)
        self.cpu_history = dpg.add_plot(label="CPU Usage History", parent=self.window)
        self.memory_history = dpg.add_plot(label="Memory Usage History", parent=self.window)
        self.cpu_x_axis = dpg.add_plot_axis(axis=0, label="Time", parent=self.cpu_history)
        self.cpu_y_axis = dpg.add_plot_axis(axis=1, label="CPU Usage", parent=self.cpu_history)
        self.memory_x_axis = dpg.add_plot_axis(axis=0, label="Time", parent=self.memory_history)
        self.memory_y_axis = dpg.add_plot_axis(axis=1, label="Memory Usage", parent=self.memory_history)
        self.cpu_line_series = None
        self.memory_line_series = None
        self.cpu_data = []
        self.memory_data = []
        self.update_task = asyncio.create_task(self.update_resource_usage())

    async def update_resource_usage(self):
        while True:
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().percent
            self.cpu_data.append(cpu_usage)
            self.memory_data.append(memory_usage)
            dpg.set_value(self.cpu_text, f"CPU Usage: {cpu_usage}%")
            dpg.set_value(self.memory_text, f"Memory Usage: {memory_usage}%")

            if self.cpu_line_series:
                dpg.delete_item(self.cpu_line_series)
            if self.memory_line_series:
                dpg.delete_item(self.memory_line_series)

            x_data = list(range(len(self.cpu_data)))  # Generate list of indices
            self.cpu_line_series = dpg.add_line_series(x_data, self.cpu_data, label="CPU Usage",
                                                       parent=self.cpu_y_axis)
            self.memory_line_series = dpg.add_line_series(x_data, self.memory_data, label="Memory Usage",
                                                          parent=self.memory_y_axis)

            await asyncio.sleep(1)
import asyncio
import dearpygui.dearpygui as dpg
from neurobehavioral_analytics_suite.gui.modules.OperationModule import OperationModule
from neurobehavioral_analytics_suite.operation_manager.OperationControl import OperationControl
from neurobehavioral_analytics_suite.operation_manager.operations.CustomOperation import CustomOperation


class OperationManagerDialog:
    """A class to manage the dialog for displaying and controlling operations."""

    SLEEP_DURATION = 0.05
    TILE_WIDTH = 300  # Fixed width for each operation tile
    TILE_HEIGHT = 300  # Fixed height for each operation tile

    def __init__(self, operation_control: OperationControl, logger, container_width=900):
        """Initializes the OperationManagerDialog with the given operation control, logger, and container width.

        Args:
            operation_control: Control interface for operations.
            logger: Logger instance for logging messages.
            container_width: Initial width of the container.
        """
        self.window = dpg.add_group(label="Operation Manager", parent="operation_pane", tag="operation_gallery",
                                    horizontal=False)
        self.operation_control = operation_control
        self.logger = logger
        self.operation_items = {}  # Store operation GUI items
        self.update_operation = None
        self.container_width = container_width
        self.tiles_per_row = self.calculate_tiles_per_row(container_width)
        self.current_row_group = None

    def calculate_tiles_per_row(self, width):
        """Calculates the number of tiles per row based on the container width.

        Args:
            width: Width of the container.

        Returns:
            Number of tiles that fit in the given width.
        """
        return max(1, width // self.TILE_WIDTH) - 1

    async def initialize(self):
        """Initializes the operation manager dialog by adding the update operation."""
        self.update_operation = await self.add_update_operation()
        dpg.set_viewport_resize_callback(self.on_resize)

    async def add_update_operation(self):
        """Adds an update operations to the operations manager.

        Returns:
            The created update operations or None if an error occurred.
        """
        try:
            operation = await self.operation_control.operation_manager.add_operation(
                operation_type=CustomOperation, name="gui_OperationManagerUpdateTask",
                local_vars=self.operation_control.local_vars, error_handler=self.operation_control.error_handler,
                func=self.display_operations, persistent=True)
            return operation
        except Exception as e:
            self.logger.error(f"Error creating task: {e}")
        return None

    async def display_operations(self):
        """Continuously checks for new operations and displays them in the GUI."""
        while True:
            # Check for new operations
            queue_copy = set(self.operation_control.queue.queue)
            for operation_chain in queue_copy:
                for node in operation_chain:
                    if node.operation not in self.operation_items and node.operation.name != "gui_OperationUpdateTask":
                        self.operation_items[node.operation] = OperationModule(node.operation, self.operation_control,
                                                                               self.logger)
                        await self.operation_items[node.operation].initialize()
                        self.add_operation_tile(node.operation)
            await asyncio.sleep(self.SLEEP_DURATION)

    def add_operation_tile(self, operation):
        """Adds a new operations tile to the GUI.

        Args:
            operation: The operations to add as a tile.
        """
        # Ensure current row group is created
        if (self.current_row_group is None
                or len(dpg.get_item_children(self.current_row_group)[1]) >= self.tiles_per_row):
            self.current_row_group = dpg.add_group(horizontal=True, parent=self.window)
            self.logger.debug(f"Created new row group: {self.current_row_group}")
        child_window = dpg.add_child_window(width=self.TILE_WIDTH, height=self.TILE_HEIGHT,
                                            parent=self.current_row_group)
        self.logger.debug(f"Created child window: {child_window} in row group: {self.current_row_group}")
        self.operation_items[operation].draw(parent=child_window)

    def on_resize(self, sender, data):
        """Handles the resize event and adjusts the number of tiles per row.

        Args:
            sender: The sender of the event.
            data: The data associated with the event.
        """
        new_width = dpg.get_viewport_client_width()
        new_tiles_per_row = self.calculate_tiles_per_row(new_width)
        if new_tiles_per_row != self.tiles_per_row:
            self.tiles_per_row = new_tiles_per_row
            self.refresh_display()

    def refresh_display(self):
        """Refreshes the display to adjust the tiles per row."""
        dpg.delete_item(self.window, children_only=True)
        self.current_row_group = None
        for operation in self.operation_items.values():
            self.add_operation_tile(operation.operation)

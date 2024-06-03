import asyncio
import dearpygui.dearpygui as dpg
from neurobehavioral_analytics_suite.gui.module.OperationModule import OperationModule
from neurobehavioral_analytics_suite.operation_manager.OperationControl import OperationControl
from neurobehavioral_analytics_suite.operation_manager.operation.CustomOperation import CustomOperation


class OperationManagerDialog:
    """A class to manage the dialog for displaying and controlling operations."""

    SLEEP_DURATION = 0.05
    TILE_WIDTH = 300  # Fixed width for each operation tile
    TILE_HEIGHT = 300  # Fixed height for each operation tile

    def __init__(self, operation_control: OperationControl, logger, tiles_per_row=3):
        """Initializes the OperationManagerDialog with the given operation control, logger, and tile settings.

        Args:
            operation_control: Control interface for operations.
            logger: Logger instance for logging messages.
            tiles_per_row: Number of tiles to display per row.
        """
        self.window = dpg.add_group(label="Operation Manager", parent="operation_pane", tag="operation_gallery",
                                    horizontal=False)
        self.operation_control = operation_control
        self.logger = logger
        self.operation_items = {}  # Store operation GUI items
        self.update_operation = None
        self.tiles_per_row = tiles_per_row
        self.current_row_group = None

    async def initialize(self):
        """Initializes the operation manager dialog by adding the update operation."""
        self.update_operation = await self.add_update_operation()

    async def add_update_operation(self):
        """Adds an update operation to the operation manager.

        Returns:
            The created update operation or None if an error occurred.
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
        """Adds a new operation tile to the GUI.

        Args:
            operation: The operation to add as a tile.
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
        
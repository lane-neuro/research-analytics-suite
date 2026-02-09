"""
NotificationPanel Module

Displays real-time notifications for operation completions, errors, suggestions, and other events.
Provides actionable buttons for quick access to results and visualizations.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
import dearpygui.dearpygui as dpg

from research_analytics_suite.gui.GUIBase import GUIBase
from research_analytics_suite.gui.modules.NotificationBus import notification_bus
from research_analytics_suite.operation_manager.operations.system.UpdateMonitor import UpdateMonitor


class NotificationTemplate:
    """Template defining appearance and behavior for notification types."""

    TEMPLATES = {
        "operation_complete": {
            "icon": "[OK]",
            "title_prefix": "NEW RESULT",
            "color": (100, 255, 100),
            "priority": "high",
            "auto_dismiss": False,
            "auto_dismiss_timeout": 0,
            "sound": False
        },
        "operation_error": {
            "icon": "[X]",
            "title_prefix": "ERROR",
            "color": (255, 100, 100),
            "priority": "critical",
            "auto_dismiss": False,
            "auto_dismiss_timeout": 0,
            "sound": True
        },
        "operation_waiting": {
            "icon": "[!]",
            "title_prefix": "INPUT NEEDED",
            "color": (255, 255, 100),
            "priority": "high",
            "auto_dismiss": False,
            "auto_dismiss_timeout": 0,
            "sound": False
        },
        "data_ready": {
            "icon": "[i]",
            "title_prefix": "DATA READY",
            "color": (100, 200, 255),
            "priority": "medium",
            "auto_dismiss": True,
            "auto_dismiss_timeout": 30,
            "sound": False
        },
        "suggestion_available": {
            "icon": "[*]",
            "title_prefix": "SUGGESTION",
            "color": (255, 200, 100),
            "priority": "medium",
            "auto_dismiss": True,
            "auto_dismiss_timeout": 120,
            "sound": False
        },
        "workflow_milestone": {
            "icon": "[OK]",
            "title_prefix": "MILESTONE",
            "color": (150, 255, 150),
            "priority": "medium",
            "auto_dismiss": True,
            "auto_dismiss_timeout": 60,
            "sound": False
        },
        "performance_warning": {
            "icon": "[!]",
            "title_prefix": "PERFORMANCE",
            "color": (255, 200, 0),
            "priority": "low",
            "auto_dismiss": True,
            "auto_dismiss_timeout": 60,
            "sound": False
        }
    }

    @staticmethod
    def get_template(notification_type: str) -> Dict[str, Any]:
        """Get template for a notification type."""
        return NotificationTemplate.TEMPLATES.get(
            notification_type,
            {
                "icon": "•",
                "title_prefix": "NOTIFICATION",
                "color": (200, 200, 200),
                "priority": "low",
                "auto_dismiss": True,
                "auto_dismiss_timeout": 30,
                "sound": False
            }
        )


class Notification:
    def __init__(self, notification_type: str, message: str, data: Dict[str, Any] = None):
        template = NotificationTemplate.get_template(notification_type)

        self.id = f"notif_{id(self)}"
        self.type = notification_type
        self.priority = template["priority"]
        self.title = template["title_prefix"]
        self.icon = template["icon"]
        self.color = template["color"]
        self.message = message
        self.data = data or {}
        self.timestamp = datetime.now()
        self.is_read = False
        self.auto_dismiss = template["auto_dismiss"]
        self.auto_dismiss_timeout = template["auto_dismiss_timeout"]
        self.sound = template["sound"]
        self.dismiss_time = None

        if self.auto_dismiss:
            from datetime import timedelta
            self.dismiss_time = self.timestamp + timedelta(seconds=self.auto_dismiss_timeout)


class NotificationPanel(GUIBase):
    """
    Notification panel for displaying real-time system and operation notifications.
    """

    def __init__(self, width: int, height: int, parent: str):
        super().__init__(width, height, parent)
        self._panel_id = f"notification_panel_{self._runtime_id}"
        self._notification_list_id = f"notification_list_{self._runtime_id}"

        self._notifications: List[Notification] = []
        self._max_notifications = 20
        self._update_operation: Optional[UpdateMonitor] = None

        self._filter_current = "all"
        self._show_settings = False
        self._needs_redraw = False  # Flag to track when redraw is needed
        self._last_notification_count = 0  # Track notification count changes

    async def initialize_gui(self) -> None:
        """Initialize notification panel and subscribe to events."""
        self._logger.debug("Initializing NotificationPanel")

        notification_bus.subscribe("operation_complete", self._on_operation_complete)
        notification_bus.subscribe("operation_error", self._on_operation_error)
        notification_bus.subscribe("operation_waiting", self._on_operation_waiting)
        notification_bus.subscribe("data_ready", self._on_data_ready)
        notification_bus.subscribe("suggestion_available", self._on_suggestion)

        await notification_bus.start()

        self._update_operation = await self._operation_control.operation_manager.create_operation(
            operation_type=UpdateMonitor,
            name=f"notification_update_{self._runtime_id}",
            action=self._update_async
        )
        self._update_operation.is_ready = True

    async def resize_gui(self, new_width: int, new_height: int) -> None:
        """Resize the notification panel."""
        self.width = new_width
        self.height = new_height

        if dpg.does_item_exist(self._panel_id):
            dpg.set_item_width(self._panel_id, new_width)
            dpg.set_item_height(self._panel_id, new_height)

    def draw(self) -> None:
        """Draw the notification panel interface."""
        with dpg.child_window(tag=self._panel_id, parent=self._parent,
                             width=self.width, height=self.height, border=False):
            self._draw_header()
            dpg.add_separator()
            self._draw_notification_list()

    def _draw_header(self) -> None:
        """Draw the panel header with title and count."""
        with dpg.group(horizontal=True):
            unread_count = sum(1 for n in self._notifications if not n.is_read)
            dpg.add_text(f"NOTIFICATIONS ({unread_count})", color=(255, 255, 255))

            dpg.add_spacer(width=10)

            if dpg.does_item_exist(f"clear_all_btn_{self._runtime_id}"):
                dpg.delete_item(f"clear_all_btn_{self._runtime_id}")

            dpg.add_button(
                label="Clear Read",
                tag=f"clear_all_btn_{self._runtime_id}",
                callback=self._clear_read_notifications,
                small=True
            )

        self._draw_filter_tabs()

    def _draw_filter_tabs(self) -> None:
        """Draw filter tabs for notification types."""
        filter_tab_id = f"filter_tabs_{self._runtime_id}"

        if dpg.does_item_exist(filter_tab_id):
            dpg.delete_item(filter_tab_id)

        with dpg.group(tag=filter_tab_id, horizontal=True):
            filters = [
                ("all", "All"),
                ("operation_complete", "Operations"),
                ("data_ready", "Data"),
                ("suggestion_available", "Suggestions")
            ]

            for filter_key, filter_label in filters:
                is_active = self._filter_current == filter_key
                color = (100, 150, 255) if is_active else (150, 150, 150)

                dpg.add_button(
                    label=filter_label,
                    callback=lambda s, a, u: self._set_filter(u),
                    user_data=filter_key,
                    small=True
                )

                if is_active:
                    dpg.bind_item_theme(dpg.last_item(), self._create_active_button_theme())

    def _create_active_button_theme(self):
        """Create theme for active filter button."""
        theme_id = f"active_filter_theme_{self._runtime_id}"

        if dpg.does_item_exist(theme_id):
            return theme_id

        with dpg.theme(tag=theme_id):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (60, 90, 150))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (70, 100, 160))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (50, 80, 140))

        return theme_id

    def _set_filter(self, filter_type: str) -> None:
        """Set the current notification filter."""
        if self._filter_current != filter_type:
            self._filter_current = filter_type
            self._needs_redraw = True  # Trigger redraw on filter change
            self._logger.debug(f"Filter changed to: {filter_type}")

    def _draw_notification_list(self) -> None:
        """Draw the scrollable list of notifications."""
        if not dpg.does_item_exist(self._panel_id):
            return

        if dpg.does_item_exist(self._notification_list_id):
            dpg.delete_item(self._notification_list_id)

        filtered_notifications = self._get_filtered_notifications()

        with dpg.child_window(tag=self._notification_list_id, height=-1, border=False, parent=self._panel_id):
            if not filtered_notifications:
                dpg.add_spacer(height=20)
                filter_text = "this filter" if self._filter_current != "all" else ""
                dpg.add_text(f"No notifications {filter_text}", color=(128, 128, 128))
                if self._filter_current == "all":
                    dpg.add_text("All operations running smoothly", color=(128, 128, 128))
            else:
                for notification in sorted(filtered_notifications,
                                         key=lambda n: n.timestamp, reverse=True):
                    self._draw_notification_item(notification)

    def _get_filtered_notifications(self) -> List[Notification]:
        """Get notifications filtered by current filter."""
        if self._filter_current == "all":
            return self._notifications

        return [n for n in self._notifications if n.type == self._filter_current]

    def _draw_notification_item(self, notification: Notification) -> None:
        """Draw a single notification item."""
        item_id = f"notif_item_{notification.id}"

        if dpg.does_item_exist(item_id):
            dpg.delete_item(item_id)

        with dpg.group(tag=item_id):
            with dpg.group(horizontal=True):
                dpg.add_text(f"{notification.icon} {notification.title}",
                           color=notification.color)
                dpg.add_spacer(width=10)
                time_str = notification.timestamp.strftime("%I:%M%p").lower()
                dpg.add_text(time_str, color=(150, 150, 150))

            dpg.add_text(notification.message, wrap=self.width - 40,
                        color=(200, 200, 200) if notification.is_read else (255, 255, 255))

            self._draw_notification_actions(notification)

            dpg.add_separator()
            dpg.add_spacer(height=5)

    def _draw_notification_actions(self, notification: Notification) -> None:
        """Draw action buttons for a notification."""
        with dpg.group(horizontal=True, horizontal_spacing=5):
            if notification.type == "operation_complete":
                dpg.add_button(
                    label="View Result",
                    callback=lambda: self._handle_view_result(notification),
                    small=True
                )
                dpg.add_button(
                    label="Visualize",
                    callback=lambda: self._handle_visualize(notification),
                    small=True
                )
            elif notification.type == "operation_error":
                dpg.add_button(
                    label="View Log",
                    callback=lambda: self._handle_view_log(notification),
                    small=True
                )
            elif notification.type == "suggestion_available":
                dpg.add_button(
                    label="Learn More",
                    callback=lambda: self._handle_learn_more(notification),
                    small=True
                )

            dpg.add_button(
                label="Dismiss",
                callback=lambda: self._dismiss_notification(notification),
                small=True
            )

    def _on_operation_complete(self, data: Dict[str, Any]) -> None:
        """Handle operation completion event."""
        notification = Notification(
            notification_type="operation_complete",
            message=f"{data.get('operation_name', 'Operation')} completed",
            data=data
        )
        self._add_notification(notification)

    def _on_operation_error(self, data: Dict[str, Any]) -> None:
        """Handle operation error event."""
        notification = Notification(
            notification_type="operation_error",
            message=f"{data.get('operation_name', 'Operation')} failed\n{data.get('error_message', '')}",
            data=data
        )
        self._add_notification(notification)

    def _on_operation_waiting(self, data: Dict[str, Any]) -> None:
        """Handle operation waiting event."""
        notification = Notification(
            notification_type="operation_waiting",
            message=f"{data.get('operation_name', 'Operation')} waiting for input",
            data=data
        )
        self._add_notification(notification)

    def _on_data_ready(self, data: Dict[str, Any]) -> None:
        """Handle data ready event."""
        notification = Notification(
            notification_type="data_ready",
            message=f"{data.get('filename', 'Data')} loaded successfully",
            data=data
        )
        self._add_notification(notification)

    def _on_suggestion(self, data: Dict[str, Any]) -> None:
        """Handle AI suggestion event."""
        notification = Notification(
            notification_type="suggestion_available",
            message=data.get('message', 'Consider optimizing your workflow'),
            data=data
        )
        self._add_notification(notification)

    def _add_notification(self, notification: Notification) -> None:
        """Add a new notification to the list with priority sorting."""
        self._notifications.append(notification)
        self._sort_notifications_by_priority()

        if len(self._notifications) > self._max_notifications:
            self._notifications = self._notifications[:self._max_notifications]

        self._needs_redraw = True  # Trigger redraw when notification added
        self._logger.debug(f"Added notification: {notification.title} (priority: {notification.priority})")

    def _sort_notifications_by_priority(self) -> None:
        """Sort notifications by priority and timestamp."""
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}

        self._notifications.sort(
            key=lambda n: (priority_order.get(n.priority, 4), -n.timestamp.timestamp())
        )

    def _dismiss_notification(self, notification: Notification) -> None:
        """Dismiss a specific notification."""
        if notification in self._notifications:
            self._notifications.remove(notification)
            self._needs_redraw = True  # Trigger redraw when notification dismissed

    def _clear_read_notifications(self) -> None:
        """Clear all read notifications."""
        self._notifications = [n for n in self._notifications if not n.is_read]
        self._needs_redraw = True  # Trigger redraw when clearing notifications

    def _handle_view_result(self, notification: Notification) -> None:
        """Handle view result action - show operation results in popup."""
        notification.is_read = True
        self._needs_redraw = True  # Trigger redraw when notification read status changes

        operation_name = notification.data.get('operation_name', 'Unknown')
        result = notification.data.get('result', {})

        popup_id = f"result_popup_{notification.id}"
        if dpg.does_item_exist(popup_id):
            dpg.delete_item(popup_id)

        with dpg.window(label=f"Results - {operation_name}",
                       tag=popup_id,
                       width=500,
                       height=400,
                       modal=True,
                       show=True,
                       pos=(100, 100)):

            dpg.add_text(f"Operation: {operation_name}", color=(200, 200, 255))
            dpg.add_text(f"Completed: {notification.timestamp.strftime('%Y-%m-%d %I:%M:%S %p')}",
                        color=(150, 150, 150))
            dpg.add_separator()
            dpg.add_spacer(height=10)

            dpg.add_text("Results:", color=(200, 200, 200))

            with dpg.child_window(height=-40, border=True):
                if isinstance(result, dict):
                    for key, value in result.items():
                        dpg.add_text(f"{key}:", color=(150, 200, 255))
                        dpg.add_text(f"  {str(value)[:500]}", wrap=460)
                        dpg.add_spacer(height=5)
                else:
                    dpg.add_text(str(result)[:1000], wrap=460)

            with dpg.group(horizontal=True):
                dpg.add_button(label="Close", callback=lambda: dpg.delete_item(popup_id), width=100)
                dpg.add_button(label="Copy", callback=lambda: self._copy_to_clipboard(str(result)), width=100)

        self._logger.info(f"Showing results for: {operation_name}")

    def _handle_visualize(self, notification: Notification) -> None:
        """Handle visualize action - trigger visualization creation."""
        notification.is_read = True
        self._needs_redraw = True  # Trigger redraw when notification read status changes

        notification_bus.publish("create_visualization", {
            "operation_id": notification.data.get('operation_id'),
            "operation_name": notification.data.get('operation_name'),
            "result": notification.data.get('result'),
            "output_ids": notification.data.get('output_ids', {})
        })

        self._logger.info(f"Triggered visualization for: {notification.data.get('operation_name')}")

    def _handle_view_log(self, notification: Notification) -> None:
        """Handle view log action - show error details."""
        notification.is_read = True
        self._needs_redraw = True  # Trigger redraw when notification read status changes

        operation_name = notification.data.get('operation_name', 'Unknown')
        error_message = notification.data.get('error_message', 'No details available')
        error_type = notification.data.get('error_type', 'Exception')

        popup_id = f"error_popup_{notification.id}"
        if dpg.does_item_exist(popup_id):
            dpg.delete_item(popup_id)

        with dpg.window(label=f"Error Details - {operation_name}",
                       tag=popup_id,
                       width=600,
                       height=400,
                       modal=True,
                       show=True,
                       pos=(100, 100)):

            dpg.add_text(f"Operation: {operation_name}", color=(255, 150, 150))
            dpg.add_text(f"Error Type: {error_type}", color=(255, 100, 100))
            dpg.add_text(f"Time: {notification.timestamp.strftime('%Y-%m-%d %I:%M:%S %p')}",
                        color=(150, 150, 150))
            dpg.add_separator()
            dpg.add_spacer(height=10)

            dpg.add_text("Error Message:", color=(200, 200, 200))
            with dpg.child_window(height=200, border=True):
                dpg.add_text(error_message, wrap=580, color=(255, 200, 200))

            dpg.add_spacer(height=10)
            dpg.add_text("Suggestions:", color=(200, 200, 200))
            with dpg.child_window(height=-40, border=True):
                suggestions = self._get_error_suggestions(error_type, error_message)
                for i, suggestion in enumerate(suggestions, 1):
                    dpg.add_text(f"{i}. {suggestion}", wrap=580, color=(200, 255, 200))

            dpg.add_button(label="Close", callback=lambda: dpg.delete_item(popup_id), width=100)

        self._logger.info(f"Showing error details for: {operation_name}")

    def _handle_learn_more(self, notification: Notification) -> None:
        """Handle learn more action - show suggestion details."""
        notification.is_read = True
        self._needs_redraw = True  # Trigger redraw when notification read status changes

        message = notification.message
        popup_id = f"suggestion_popup_{notification.id}"

        if dpg.does_item_exist(popup_id):
            dpg.delete_item(popup_id)

        with dpg.window(label="AI Suggestion Details",
                       tag=popup_id,
                       width=500,
                       height=300,
                       modal=True,
                       show=True,
                       pos=(150, 150)):

            dpg.add_text("[*] Suggestion", color=(255, 200, 100))
            dpg.add_separator()
            dpg.add_spacer(height=10)

            with dpg.child_window(height=-40, border=False):
                dpg.add_text(message, wrap=480)

                if 'operation_type' in notification.data:
                    dpg.add_spacer(height=20)
                    dpg.add_text(f"Recommended Operation: {notification.data['operation_type']}",
                               color=(150, 200, 255))

            with dpg.group(horizontal=True):
                dpg.add_button(label="Apply Suggestion",
                             callback=lambda: self._apply_suggestion(notification),
                             width=150)
                dpg.add_button(label="Close",
                             callback=lambda: dpg.delete_item(popup_id),
                             width=100)

        self._logger.info(f"Showing suggestion details: {notification.title}")

    def _copy_to_clipboard(self, text: str) -> None:
        """Copy text to clipboard."""
        try:
            import pyperclip
            pyperclip.copy(text)
            self._logger.info("Copied to clipboard")
        except ImportError:
            self._logger.warning("pyperclip not available - cannot copy to clipboard")
        except Exception as e:
            self._logger.error(f"Failed to copy to clipboard: {e}")

    def _get_error_suggestions(self, error_type: str, error_message: str) -> List[str]:
        """Get suggestions for fixing an error."""
        suggestions = []

        if "not found" in error_message.lower() or "filenotfound" in error_type.lower():
            suggestions.append("Check that the file path is correct and the file exists")
            suggestions.append("Verify you have read permissions for the file")

        if "type" in error_type.lower() or "incompatible" in error_message.lower():
            suggestions.append("Check input data types match operation requirements")
            suggestions.append("Consider adding a type conversion operation before this step")

        if "memory" in error_message.lower() or "outofmemory" in error_type.lower():
            suggestions.append("Try processing data in smaller batches")
            suggestions.append("Consider enabling GPU acceleration if available")

        if "value" in error_type.lower():
            suggestions.append("Verify input values are within valid ranges")
            suggestions.append("Check for missing or null values in your data")

        if not suggestions:
            suggestions.append("Review the operation's input requirements")
            suggestions.append("Check the operation logs for more details")
            suggestions.append("Try resetting the operation and running again")

        return suggestions

    def _apply_suggestion(self, notification: Notification) -> None:
        """Apply an AI suggestion."""
        operation_type = notification.data.get('operation_type')

        if operation_type:
            notification_bus.publish("apply_suggestion", {
                "operation_type": operation_type,
                "context": notification.data
            })
            self._logger.info(f"Applied suggestion: {operation_type}")
        else:
            self._logger.warning("No operation type in suggestion data")

    async def _update_async(self) -> None:
        """Async update loop for refreshing the panel - only redraws when needed."""
        while self._update_operation and self._update_operation.is_ready:
            self._check_auto_dismiss()

            # Only redraw when notifications actually change
            if dpg.does_item_exist(self._panel_id) and self._needs_redraw:
                self._draw_notification_list()
                self._needs_redraw = False

            await asyncio.sleep(0.5)

    def _check_auto_dismiss(self) -> None:
        """Check and remove auto-dismiss notifications that have expired."""
        now = datetime.now()
        to_remove = []

        for notification in self._notifications:
            if notification.auto_dismiss and notification.dismiss_time:
                if now >= notification.dismiss_time:
                    to_remove.append(notification)
                    self._logger.debug(f"Auto-dismissing notification: {notification.title}")

        if to_remove:
            for notification in to_remove:
                self._notifications.remove(notification)
            self._needs_redraw = True  # Trigger redraw when auto-dismissing

    async def cleanup(self) -> None:
        """Cleanup resources when panel is destroyed."""
        if self._update_operation:
            await self._update_operation.stop()

        notification_bus.clear_subscribers()
        await notification_bus.stop()

        self._logger.debug("NotificationPanel cleanup completed")

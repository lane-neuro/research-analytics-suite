"""
IntelligencePanel Module

AI/ML Intelligence monitoring and recommendation panel for the GUI.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Development
"""
import dearpygui.dearpygui as dpg
from typing import Optional, List

from research_analytics_suite.utils.CustomLogger import CustomLogger
from research_analytics_suite.analytics.operation_intelligence.models import Recommendation


class IntelligencePanel:
    """
    AI/ML Intelligence Panel for monitoring and recommendations.

    Features:
    - Display current intelligence system status
    - Show pending recommendations
    - Accept/reject recommendations
    - View learning statistics
    - Monitor system performance
    """

    def __init__(self, parent: str, width: int = -1, height: int = -1):
        """
        Initialize intelligence panel.

        Args:
            parent: Parent DearPyGUI container
            width: Panel width
            height: Panel height
        """
        self._logger = CustomLogger()
        self._parent = parent
        self._width = width
        self._height = height

        self._intelligence_manager = None
        self._update_task = None
        self._is_running = False

        # UI tags
        self._panel_group = f"{parent}_intelligence_panel"
        self._status_text = f"{parent}_status_text"
        self._recommendations_table = f"{parent}_recommendations_table"

    async def initialize(self):
        """Initialize the intelligence panel."""
        try:
            # Get intelligence manager
            from research_analytics_suite.analytics.operation_intelligence.manager import IntelligenceManager
            self._intelligence_manager = IntelligenceManager()

            self._logger.info("Intelligence Panel initialized")

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    def draw(self):
        """Draw the intelligence panel UI."""
        try:
            with dpg.group(parent=self._parent, tag=self._panel_group):
                # Header
                dpg.add_text("AI/ML Operation Intelligence", color=(100, 200, 255))
                dpg.add_separator()

                # Status section
                with dpg.group(horizontal=True):
                    dpg.add_text("Status: ")
                    dpg.add_text("Initializing...", tag=self._status_text, color=(200, 200, 100))

                dpg.add_spacer(height=5)

                # Control buttons
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="Analyze Workspace",
                        callback=self._on_analyze_clicked,
                        width=150
                    )
                    dpg.add_button(
                        label="Refresh",
                        callback=self._on_refresh_clicked,
                        width=100
                    )

                dpg.add_spacer(height=10)
                dpg.add_separator()

                # Recommendations section
                dpg.add_text("Recommendations", color=(150, 200, 150))
                dpg.add_spacer(height=5)

                with dpg.table(
                    header_row=True,
                    tag=self._recommendations_table,
                    borders_innerH=True,
                    borders_outerH=True,
                    borders_innerV=True,
                    borders_outerV=True,
                    row_background=True,
                    scrollY=True,
                    height=300
                ):
                    # Table columns
                    dpg.add_table_column(label="Operation")
                    dpg.add_table_column(label="Confidence")
                    dpg.add_table_column(label="Actions", width_fixed=True, init_width_or_weight=150)

                dpg.add_spacer(height=10)

                # Statistics section
                with dpg.collapsing_header(label="Statistics", default_open=False):
                    dpg.add_text("Total Recommendations: ", tag=f"{self._panel_group}_total_recs")
                    dpg.add_text("Accepted: ", tag=f"{self._panel_group}_accepted")
                    dpg.add_text("Rejected: ", tag=f"{self._panel_group}_rejected")
                    dpg.add_text("Learning Model Status: ", tag=f"{self._panel_group}_model_status")

            self._logger.debug("Intelligence Panel UI drawn")

            # Start update loop
            self._start_update_loop()

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    def _start_update_loop(self):
        """Start the UI update loop."""
        import asyncio

        async def update_loop():
            while self._is_running:
                try:
                    await self._update_ui()
                    await asyncio.sleep(2)  # Update every 2 seconds
                except Exception as e:
                    self._logger.error(f"Update loop error: {e}")
                    await asyncio.sleep(5)

        self._is_running = True
        # Note: This would need proper async integration with DearPyGUI's render loop
        # For now, updates will happen on user actions

    async def _update_ui(self):
        """Update the UI with current intelligence data."""
        try:
            if not self._intelligence_manager:
                return

            # Update status
            if dpg.does_item_exist(self._status_text):
                if self._intelligence_manager.is_enabled():
                    if self._intelligence_manager.is_running():
                        dpg.set_value(self._status_text, "Running")
                        dpg.configure_item(self._status_text, color=(100, 255, 100))
                    else:
                        dpg.set_value(self._status_text, "Ready")
                        dpg.configure_item(self._status_text, color=(200, 200, 100))
                else:
                    dpg.set_value(self._status_text, "Disabled")
                    dpg.configure_item(self._status_text, color=(200, 100, 100))

            # Update recommendations table
            await self._update_recommendations_table()

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    async def _update_recommendations_table(self):
        """Update the recommendations table."""
        try:
            if not dpg.does_item_exist(self._recommendations_table):
                return

            # Clear existing rows
            children = dpg.get_item_children(self._recommendations_table, slot=1)
            if children:
                for child in children:
                    dpg.delete_item(child)

            # Get pending recommendations
            recommendations = await self._intelligence_manager.get_pending_recommendations()

            # Add rows for each recommendation
            for rec in recommendations:
                with dpg.table_row(parent=self._recommendations_table):
                    # Operation name
                    op_name = rec.operation_type.__name__ if rec.operation_type else "Unknown"
                    dpg.add_text(op_name)

                    # Confidence
                    dpg.add_text(f"{rec.confidence:.1%}")

                    # Action buttons
                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label="Accept",
                            callback=lambda s, a, u: self._on_accept_recommendation(u),
                            user_data=rec.id,
                            width=60
                        )
                        dpg.add_button(
                            label="Reject",
                            callback=lambda s, a, u: self._on_reject_recommendation(u),
                            user_data=rec.id,
                            width=60
                        )

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    def _on_analyze_clicked(self):
        """Handle analyze button click."""
        try:
            import asyncio
            asyncio.create_task(self._analyze_workspace())
        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    async def _analyze_workspace(self):
        """Trigger workspace analysis."""
        try:
            if not self._intelligence_manager:
                self._logger.warning("Intelligence manager not available")
                return

            # Get workspace
            from research_analytics_suite.data_engine.Workspace import Workspace
            workspace = Workspace()

            if not workspace._initialized:
                self._logger.warning("Workspace not initialized")
                return

            self._logger.info("Starting workspace analysis...")
            recommendations = await self._intelligence_manager.request_recommendations(workspace)
            self._logger.info(f"Analysis complete: {len(recommendations)} recommendations")

            # Update UI
            await self._update_ui()

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    def _on_refresh_clicked(self):
        """Handle refresh button click."""
        try:
            import asyncio
            asyncio.create_task(self._update_ui())
        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    def _on_accept_recommendation(self, recommendation_id: str):
        """Handle accept recommendation."""
        try:
            import asyncio
            asyncio.create_task(self._accept_recommendation(recommendation_id))
        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    async def _accept_recommendation(self, recommendation_id: str):
        """Accept a recommendation."""
        try:
            if not self._intelligence_manager:
                return

            await self._intelligence_manager.submit_feedback(recommendation_id, accepted=True)
            await self._intelligence_manager.clear_recommendation(recommendation_id)

            self._logger.info(f"Accepted recommendation: {recommendation_id}")

            # Update UI
            await self._update_ui()

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    def _on_reject_recommendation(self, recommendation_id: str):
        """Handle reject recommendation."""
        try:
            import asyncio
            asyncio.create_task(self._reject_recommendation(recommendation_id))
        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    async def _reject_recommendation(self, recommendation_id: str):
        """Reject a recommendation."""
        try:
            if not self._intelligence_manager:
                return

            await self._intelligence_manager.submit_feedback(recommendation_id, accepted=False)
            await self._intelligence_manager.clear_recommendation(recommendation_id)

            self._logger.info(f"Rejected recommendation: {recommendation_id}")

            # Update UI
            await self._update_ui()

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    def cleanup(self):
        """Cleanup panel resources."""
        self._is_running = False
        if self._update_task:
            self._update_task.cancel()

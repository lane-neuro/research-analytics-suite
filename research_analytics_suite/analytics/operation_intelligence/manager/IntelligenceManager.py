"""
IntelligenceManager Module

High-level coordinator between intelligence system and RAS.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Development
"""
import asyncio
from typing import List, Optional

from research_analytics_suite.utils.CustomLogger import CustomLogger
from research_analytics_suite.utils.Config import Config
from research_analytics_suite.data_engine.Workspace import Workspace
from research_analytics_suite.analytics.operation_intelligence.models import Recommendation


class IntelligenceManager:
    """
    High-level coordinator for operation intelligence system.

    Key Features:
    - Lifecycle management
    - Configuration handling
    - Background task scheduling
    - Integration with OperationControl
    - Feature enable/disable
    """

    _instance: Optional['IntelligenceManager'] = None
    _lock: asyncio.Lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize intelligence manager."""
        if not hasattr(self, '_initialized'):
            self._logger = CustomLogger()
            self._config: Optional[Config] = None

            self._intelligence_engine = None
            self._notifier = None

            self._is_enabled = False
            self._is_running = False

            self._initialized = False

    async def initialize(self) -> None:
        """
        Initializes intelligence manager.
        """
        if self._initialized:
            return

        self._logger.debug("Initializing Intelligence Manager")

        # Get Config singleton
        from research_analytics_suite.utils.Config import Config
        self._config = Config()
        self._is_enabled = self._config.OPERATION_INTELLIGENCE_ENABLED

        if not self._is_enabled:
            self._logger.debug("Operation Intelligence is disabled")
            return

        try:
            from research_analytics_suite.analytics.operation_intelligence.engine import IntelligenceEngine
            from research_analytics_suite.analytics.operation_intelligence.manager import SuggestionNotifier

            self._intelligence_engine = IntelligenceEngine()
            await self._intelligence_engine.initialize()

            self._notifier = SuggestionNotifier()

            self._initialized = True
            self._logger.debug("Intelligence Manager initialized successfully")

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)
            self._is_enabled = False

    async def start_intelligence_system(self) -> None:
        """
        Starts intelligence system.
        """
        if not self._is_enabled or self._is_running:
            return

        self._logger.debug("Starting intelligence system")

        try:
            await self._intelligence_engine.start_background_analysis()
            self._is_running = True

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    async def stop_intelligence_system(self) -> None:
        """
        Stops intelligence system.
        """
        if not self._is_running:
            return

        self._logger.info("Stopping intelligence system")

        try:
            await self._intelligence_engine.stop()
            self._is_running = False

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    async def request_recommendations(self, workspace: Workspace) -> List[Recommendation]:
        """
        Requests recommendations for workspace.

        Args:
            workspace: Workspace to analyze

        Returns:
            List of recommendations
        """
        if not self._is_enabled:
            return []

        try:
            recommendations = await self._intelligence_engine.analyze_workspace(workspace)

            # Queue recommendations for notification
            for rec in recommendations:
                await self._notifier.queue_recommendation(rec)

            return recommendations

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)
            return []

    async def submit_feedback(self, recommendation_id: str, accepted: bool) -> None:
        """
        Submits user feedback.

        Args:
            recommendation_id: ID of recommendation
            accepted: Whether user accepted
        """
        if not self._is_enabled:
            return

        try:
            await self._intelligence_engine.process_user_feedback(recommendation_id, accepted)

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    def is_enabled(self) -> bool:
        """
        Checks if intelligence system is enabled.

        Returns:
            True if enabled
        """
        return self._is_enabled

    def is_running(self) -> bool:
        """
        Checks if intelligence system is running.

        Returns:
            True if running
        """
        return self._is_running

    async def get_pending_recommendations(self) -> List[Recommendation]:
        """
        Gets pending recommendations from notifier.

        Returns:
            List of pending recommendations
        """
        if not self._is_enabled or not self._notifier:
            return []

        try:
            return await self._notifier.get_pending_recommendations()
        except Exception as e:
            self._logger.error(e, self.__class__.__name__)
            return []

    async def clear_recommendation(self, recommendation_id: str) -> None:
        """
        Clears a recommendation from the queue.

        Args:
            recommendation_id: ID of recommendation to clear
        """
        if not self._is_enabled or not self._notifier:
            return

        try:
            self._notifier.clear_recommendation(recommendation_id)
        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

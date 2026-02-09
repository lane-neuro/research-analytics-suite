"""
SuggestionNotifier Module

Handles communication of recommendations to users.

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
from typing import List, Dict, Any
from collections import deque

from research_analytics_suite.utils.CustomLogger import CustomLogger
from research_analytics_suite.utils.Config import Config
from research_analytics_suite.analytics.operation_intelligence.models import Recommendation


class SuggestionNotifier:
    """
    Handles communication of recommendations to users.

    Key Features:
    - Queue management for recommendations
    - Priority sorting
    - Notification formatting
    - GUI integration
    - CLI fallback support
    - Rate limiting
    """

    def __init__(self):
        """
        Initialize suggestion notifier.

        Args:
            config: Configuration object
        """
        self._logger = CustomLogger()
        from research_analytics_suite.utils.Config import Config
        self._config = Config()

        max_size = (int(self._config.RECOMMENDATION_MAX_QUEUE_SIZE)) \
            if (isinstance(self._config.RECOMMENDATION_MAX_QUEUE_SIZE, str) and
                self._config.RECOMMENDATION_MAX_QUEUE_SIZE.isdigit()) \
            else self._config.RECOMMENDATION_MAX_QUEUE_SIZE
        if max_size is None or not isinstance(max_size, int):
            max_size = 10  # Default fallback
            self._logger.warning(f"Invalid RECOMMENDATION_MAX_QUEUE_SIZE, using default: {max_size}")

        self._max_queue_size = max_size
        self._recommendation_queue: deque = deque(maxlen=self._max_queue_size)

    async def queue_recommendation(self, recommendation: Recommendation) -> None:
        """
        Adds recommendation to queue.

        Args:
            recommendation: Recommendation to queue
        """
        self._logger.info(f"Queuing recommendation: {recommendation.id}")

        if len(self._recommendation_queue) >= self._max_queue_size:
            self._logger.warning("Recommendation queue full, removing oldest")

        self._recommendation_queue.append(recommendation)

        # Notify user
        await self._notify_user(recommendation)

    async def get_pending_recommendations(self) -> List[Recommendation]:
        """
        Gets pending recommendations.

        Returns:
            List of pending recommendations
        """
        return list(self._recommendation_queue)

    def format_for_display(self, recommendation: Recommendation) -> Dict[str, Any]:
        """
        Formats recommendation for display.

        Args:
            recommendation: Recommendation to format

        Returns:
            Display data dictionary
        """
        return {
            'id': recommendation.id,
            'operation': recommendation.operation_type.__name__ if recommendation.operation_type else 'Unknown',
            'confidence': f"{recommendation.confidence:.1%}",
            'explanation': recommendation.explanation,
            'benefits': recommendation.expected_benefits,
            'timestamp': recommendation.timestamp.isoformat()
        }

    async def notify_gui(self, recommendation: Recommendation) -> None:
        """
        Notifies GUI of new recommendation.

        Args:
            recommendation: Recommendation to display
        """
        self._logger.debug("Notifying GUI of recommendation")

        # TODO: Integrate with GUI event system
        # TODO: Trigger RecommendationPanel update
        pass

    async def notify_cli(self, recommendation: Recommendation) -> None:
        """
        Notifies CLI of new recommendation.

        Args:
            recommendation: Recommendation to display
        """
        self._logger.info(
            f"New recommendation: {recommendation.operation_type.__name__ if recommendation.operation_type else 'Unknown'} "
            f"(confidence: {recommendation.confidence:.1%})"
        )

    async def _notify_user(self, recommendation: Recommendation) -> None:
        """
        Internal method to notify user.

        Args:
            recommendation: Recommendation
        """
        try:
            # Try GUI first
            await self.notify_gui(recommendation)
        except Exception:
            # Fallback to CLI
            await self.notify_cli(recommendation)

    def clear_recommendation(self, recommendation_id: str) -> None:
        """
        Clears recommendation from queue.

        Args:
            recommendation_id: ID of recommendation to clear
        """
        self._recommendation_queue = deque(
            [r for r in self._recommendation_queue if r.id != recommendation_id],
            maxlen=self._max_queue_size
        )

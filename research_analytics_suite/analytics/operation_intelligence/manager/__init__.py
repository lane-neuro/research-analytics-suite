"""
Manager Module

High-level coordination and notification for operation intelligence.

Components:
- IntelligenceManager: Coordinates intelligence system
- SuggestionNotifier: Handles user notifications

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Development
"""

from research_analytics_suite.analytics.operation_intelligence.manager.IntelligenceManager import (
    IntelligenceManager
)
from research_analytics_suite.analytics.operation_intelligence.manager.SuggestionNotifier import SuggestionNotifier

__all__ = [
    'IntelligenceManager',
    'SuggestionNotifier',
]

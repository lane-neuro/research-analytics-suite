"""
Operation Intelligence Module

AI-powered operation recommendation system that safely tests operations
in sandbox workspaces and learns from user behavior to provide intelligent
suggestions.

Key Components:
- IntelligenceEngine: Core AI/ML recommendation engine
- OperationAnalyzer: Analyzes operation patterns and compatibility
- PatternLearner: Learns from user behavior and simulation results
- OperationSimulator: Tests operations in sandbox environments
- ResultEvaluator: Evaluates simulation results
- IntelligenceManager: High-level coordinator
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

from research_analytics_suite.analytics.operation_intelligence.engine import (
    IntelligenceEngine,
    OperationAnalyzer,
    PatternLearner,
)
from research_analytics_suite.analytics.operation_intelligence.simulation import (
    OperationSimulator,
    ResultEvaluator,
)
from research_analytics_suite.analytics.operation_intelligence.manager import (
    IntelligenceManager,
    SuggestionNotifier,
)

__all__ = [
    'IntelligenceEngine',
    'OperationAnalyzer',
    'PatternLearner',
    'OperationSimulator',
    'ResultEvaluator',
    'IntelligenceManager',
    'SuggestionNotifier',
]

"""
analytics package

AI-powered operation intelligence for the Research Analytics Suite.

Available modules:
- operation_intelligence: AI-powered operation recommendation system
"""

from .operation_intelligence import (
    IntelligenceEngine,
    OperationAnalyzer,
    PatternLearner,
    OperationSimulator,
    ResultEvaluator,
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

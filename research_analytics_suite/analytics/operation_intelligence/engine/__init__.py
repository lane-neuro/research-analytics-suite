"""
Intelligence Engine Module

Core AI/ML recommendation engine for operation intelligence.

Components:
- IntelligenceEngine: Main orchestrator
- OperationAnalyzer: Analyzes operation patterns
- PatternLearner: Learns from user behavior

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Development
"""

from research_analytics_suite.analytics.operation_intelligence.engine.IntelligenceEngine import IntelligenceEngine
from research_analytics_suite.analytics.operation_intelligence.engine.OperationAnalyzer import OperationAnalyzer
from research_analytics_suite.analytics.operation_intelligence.engine.PatternLearner import PatternLearner

__all__ = [
    'IntelligenceEngine',
    'OperationAnalyzer',
    'PatternLearner',
]

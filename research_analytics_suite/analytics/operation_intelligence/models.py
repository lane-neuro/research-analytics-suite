"""
Data Models for Operation Intelligence

Shared data models used across the operation intelligence system.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Development
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Type
from datetime import datetime
from uuid import uuid4

from research_analytics_suite.operation_manager.operations.core.BaseOperation import BaseOperation
from research_analytics_suite.data_engine.core.DataProfile import DataProfile
from research_analytics_suite.data_engine.sandbox.ExecutionIsolator import ExecutionMetrics


@dataclass
class Recommendation:
    """Represents an operation recommendation."""
    id: str = field(default_factory=lambda: str(uuid4()))
    operation_type: Type[BaseOperation] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    explanation: str = ""
    expected_benefits: List[str] = field(default_factory=list)
    simulation_result: Optional['SimulationResult'] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SimulationResult:
    """Results from operation simulation."""
    operation_type: Type[BaseOperation]
    success: bool
    execution_time: float
    memory_used: float
    error: Optional[Exception] = None
    output_profile: Optional[DataProfile] = None
    metrics: Optional[ExecutionMetrics] = None


@dataclass
class UserFeedback:
    """User feedback on recommendations."""
    recommendation_id: str
    accepted: bool
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataCharacteristics:
    """Characteristics of data for operation matching."""
    data_type: str = "unknown"
    size_mb: float = 0.0
    num_rows: Optional[int] = None
    num_columns: Optional[int] = None
    has_nulls: bool = False
    numeric_columns: List[str] = field(default_factory=list)
    categorical_columns: List[str] = field(default_factory=list)
    additional_properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OperationMatch:
    """Match between operation and data."""
    operation_type: Type[BaseOperation]
    fit_score: float
    estimated_success_probability: float
    reasoning: str = ""


@dataclass
class EvaluationScore:
    """Evaluation score for simulation result."""
    overall_score: float
    performance_score: float
    correctness_score: float
    confidence: float
    should_recommend: bool
    explanation: str = ""

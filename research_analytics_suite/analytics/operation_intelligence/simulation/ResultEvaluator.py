"""
ResultEvaluator Module

Evaluates simulation results and determines recommendation quality.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Development
"""
from typing import List

from research_analytics_suite.utils.CustomLogger import CustomLogger
from research_analytics_suite.utils.Config import Config
from research_analytics_suite.analytics.operation_intelligence.models import (
    SimulationResult,
    EvaluationScore
)


class ResultEvaluator:
    """
    Evaluates simulation results and determines recommendation quality.

    Key Features:
    - Multi-dimensional evaluation
    - Confidence scoring
    - Comparative analysis
    - Threshold-based filtering
    - Explainability
    """

    def __init__(self):
        """
        Initialize result evaluator.

        Args:
            config: Configuration object
        """
        self._logger = CustomLogger()
        from research_analytics_suite.utils.Config import Config
        self._config = Config()

        self._confidence_threshold = self._config.RECOMMENDATION_CONFIDENCE_THRESHOLD

    def evaluate_result(self, result: SimulationResult) -> EvaluationScore:
        """
        Evaluates single result.

        Args:
            result: Simulation result

        Returns:
            EvaluationScore
        """
        self._logger.debug("Evaluating simulation result")

        # TODO: Multi-criteria evaluation
        performance_score = self._evaluate_performance(result)
        correctness_score = self._evaluate_correctness(result)
        confidence = self.calculate_confidence(result)

        overall_score = (performance_score + correctness_score) / 2.0
        should_recommend = self.should_recommend_from_score(overall_score, confidence)

        return EvaluationScore(
            overall_score=overall_score,
            performance_score=performance_score,
            correctness_score=correctness_score,
            confidence=confidence,
            should_recommend=should_recommend,
            explanation=self.generate_explanation(result)
        )

    def calculate_confidence(self, result: SimulationResult) -> float:
        """
        Calculates confidence score.

        Args:
            result: Simulation result

        Returns:
            Confidence score (0.0 to 1.0)
        """
        if not result.success:
            return 0.0

        confidence = 1.0

        # Reduce confidence if execution was slow
        if result.execution_time > 10.0:  # More than 10 seconds
            confidence *= 0.8
        elif result.execution_time > 30.0:  # More than 30 seconds
            confidence *= 0.6

        # Reduce confidence if memory usage was high
        if result.memory_used > 500:  # More than 500MB
            confidence *= 0.9
        elif result.memory_used > 1000:  # More than 1GB
            confidence *= 0.7

        # Reduce confidence if no output profile
        if result.output_profile is None:
            confidence *= 0.9

        # Reduce confidence if no metrics
        if result.metrics is None:
            confidence *= 0.85

        return max(0.0, min(1.0, confidence))

    def compare_results(self, results: List[SimulationResult]) -> List[SimulationResult]:
        """
        Compares and ranks multiple results.

        Args:
            results: List of simulation results

        Returns:
            Ranked list of results
        """
        self._logger.debug(f"Comparing {len(results)} results")

        # TODO: Implement ranking algorithm
        scored_results = [(r, self.evaluate_result(r)) for r in results]
        ranked = sorted(scored_results, key=lambda x: x[1].overall_score, reverse=True)

        return [r[0] for r in ranked]

    def should_recommend(self, score: EvaluationScore) -> bool:
        """
        Determines if result should be recommended.

        Args:
            score: Evaluation score

        Returns:
            True if should recommend
        """
        return score.confidence >= self._confidence_threshold

    def should_recommend_from_score(self, overall_score: float, confidence: float) -> bool:
        """
        Determines if should recommend based on score and confidence.

        Args:
            overall_score: Overall evaluation score
            confidence: Confidence level

        Returns:
            True if should recommend
        """
        return (
            overall_score >= 0.7 and
            confidence >= self._confidence_threshold
        )

    def generate_explanation(self, result: SimulationResult) -> str:
        """
        Generates human-readable explanation.

        Args:
            result: Simulation result

        Returns:
            Explanation string
        """
        if not result.success:
            error_msg = str(result.error) if result.error else "Unknown error"
            return f"Operation failed during simulation: {error_msg}"

        # Build explanation for successful operation
        parts = [f"Operation completed successfully"]

        # Add performance metrics
        if result.execution_time > 0:
            parts.append(f"in {result.execution_time:.2f}s")

        if result.memory_used > 0:
            parts.append(f"using {result.memory_used:.1f}MB memory")

        # Add quality assessment
        if result.execution_time < 1.0:
            parts.append("(fast execution)")
        elif result.execution_time > 30.0:
            parts.append("(slow execution)")

        if result.memory_used < 100:
            parts.append("(low memory usage)")
        elif result.memory_used > 1000:
            parts.append("(high memory usage)")

        return " ".join(parts)

    def _evaluate_performance(self, result: SimulationResult) -> float:
        """
        Evaluates performance aspects.

        Args:
            result: Simulation result

        Returns:
            Performance score (0.0 to 1.0)
        """
        if not result.success:
            return 0.0

        score = 1.0

        # Evaluate execution time (weight: 0.6)
        time_score = 1.0
        if result.execution_time < 1.0:
            time_score = 1.0  # Excellent
        elif result.execution_time < 5.0:
            time_score = 0.9  # Good
        elif result.execution_time < 10.0:
            time_score = 0.7  # Acceptable
        elif result.execution_time < 30.0:
            time_score = 0.5  # Slow
        else:
            time_score = 0.3  # Very slow

        # Evaluate memory usage (weight: 0.4)
        memory_score = 1.0
        if result.memory_used < 100:
            memory_score = 1.0  # Excellent
        elif result.memory_used < 500:
            memory_score = 0.9  # Good
        elif result.memory_used < 1000:
            memory_score = 0.7  # Acceptable
        else:
            memory_score = 0.5  # High

        # Weighted average
        score = (time_score * 0.6) + (memory_score * 0.4)

        return max(0.0, min(1.0, score))

    def _evaluate_correctness(self, result: SimulationResult) -> float:
        """
        Evaluates correctness of result.

        Args:
            result: Simulation result

        Returns:
            Correctness score (0.0 to 1.0)
        """
        if not result.success:
            return 0.0

        score = 1.0

        # Check if we have output
        if result.output_profile is None:
            score *= 0.8  # Reduce score if no output

        # Check if we have metrics
        if result.metrics is None:
            score *= 0.9  # Reduce score if no metrics

        # Check if error occurred despite success flag
        if result.error is not None:
            score *= 0.7  # Suspicious - success but has error

        return max(0.0, min(1.0, score))

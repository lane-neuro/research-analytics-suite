"""
OperationAnalyzer Module

Analyzes data characteristics and matches them with compatible operations.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Development
"""
from typing import List, Type

from research_analytics_suite.utils.CustomLogger import CustomLogger
from research_analytics_suite.utils.Config import Config
from research_analytics_suite.data_engine.core.DataProfile import DataProfile
from research_analytics_suite.operation_manager.operations.core.BaseOperation import BaseOperation
from research_analytics_suite.analytics.operation_intelligence.models import (
    DataCharacteristics,
    OperationMatch
)


class OperationAnalyzer:
    """
    Analyzes data and matches with compatible operations.

    Key Features:
    - Data profiling and characterization
    - Operation library analysis
    - Compatibility matching
    - Success probability estimation
    """

    def __init__(self):
        """
        Initialize operation analyzer.

        Args:
            config: Configuration object
        """
        self._logger = CustomLogger()
        from research_analytics_suite.utils.Config import Config
        self._config = Config()

    async def analyze_data_profile(self, profile: DataProfile) -> DataCharacteristics:
        """
        Analyzes data characteristics from profile.

        Args:
            profile: DataProfile to analyze

        Returns:
            DataCharacteristics object
        """
        self._logger.debug("Analyzing data profile")

        try:
            # Extract characteristics from DataProfile
            characteristics = DataCharacteristics(
                data_type=profile.data_type,
                size_mb=profile.size_mb,
                has_nulls=profile.characteristics.get('has_nulls', False) if profile.characteristics else False,
            )

            # Extract schema information if available
            if profile.schema:
                characteristics.num_rows = profile.schema.get('num_rows')
                characteristics.num_columns = profile.schema.get('num_columns')

                # Identify column types
                columns = profile.schema.get('columns', {})
                for col_name, col_info in columns.items():
                    col_type = col_info.get('type', 'unknown')
                    if col_type in ['int', 'float', 'double', 'numeric']:
                        characteristics.numeric_columns.append(col_name)
                    elif col_type in ['str', 'string', 'categorical', 'object']:
                        characteristics.categorical_columns.append(col_name)

            # Store additional properties from profile
            if profile.characteristics:
                characteristics.additional_properties = profile.characteristics.copy()

            self._logger.debug(f"Analyzed data profile: {characteristics.data_type}, {characteristics.size_mb:.2f} MB")
            return characteristics

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)
            return DataCharacteristics()

    async def find_compatible_operations(
        self,
        characteristics: DataCharacteristics
    ) -> List[OperationMatch]:
        """
        Finds operations compatible with data characteristics.

        Args:
            characteristics: Data characteristics

        Returns:
            List of compatible operations with scores
        """
        self._logger.debug("Finding compatible operations")

        matches = []

        try:
            # Get library manifest to access operations
            from research_analytics_suite.library_manifest.LibraryManifest import LibraryManifest
            library_manifest = LibraryManifest()

            if not hasattr(library_manifest, '_library') or not library_manifest._library:
                self._logger.warning("Library manifest not initialized or empty")
                return matches

            # Iterate through available operations
            for operation_name, operation_data in library_manifest._library.items():
                try:
                    # Get operation class
                    operation_type = operation_data.get('class') if isinstance(operation_data, dict) else None

                    if operation_type and isinstance(operation_type, type) and issubclass(operation_type, BaseOperation):
                        # Score the operation fit
                        fit_score = self.score_operation_fit(operation_type, characteristics)

                        # Only include operations with reasonable fit
                        if fit_score >= 0.3:  # 30% threshold
                            # Estimate success probability
                            success_prob = fit_score * 0.8  # Simple heuristic for now

                            match = OperationMatch(
                                operation_type=operation_type,
                                fit_score=fit_score,
                                estimated_success_probability=success_prob,
                                reasoning=f"Data type compatibility and size appropriateness"
                            )
                            matches.append(match)

                except Exception as e:
                    self._logger.warning(f"Failed to evaluate operation {operation_name}: {e}")

            # Sort by fit score descending
            matches.sort(key=lambda x: x.fit_score, reverse=True)

            self._logger.debug(f"Found {len(matches)} compatible operations")
            return matches

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)
            return matches

    def score_operation_fit(
        self,
        operation: Type[BaseOperation],
        characteristics: DataCharacteristics
    ) -> float:
        """
        Scores how well an operation fits the data.

        Args:
            operation: Operation type
            characteristics: Data characteristics

        Returns:
            Fit score (0.0 to 1.0)
        """
        try:
            score = 0.0
            weight_sum = 0.0

            # Check operation attributes if available
            if hasattr(operation, 'operation_attributes'):
                attrs = operation.operation_attributes

                # Data type compatibility (weight: 0.4)
                if hasattr(attrs, 'input_data_types'):
                    input_types = attrs.input_data_types if isinstance(attrs.input_data_types, list) else []
                    if characteristics.data_type in input_types or 'any' in input_types:
                        score += 0.4
                    elif len(input_types) == 0:  # No restriction
                        score += 0.2
                    weight_sum += 0.4

                # Size appropriateness (weight: 0.3)
                if hasattr(attrs, 'recommended_max_size_mb'):
                    max_size = attrs.recommended_max_size_mb
                    if characteristics.size_mb <= max_size:
                        score += 0.3
                    elif characteristics.size_mb <= max_size * 1.5:  # Within 50% over
                        score += 0.15
                    weight_sum += 0.3
                else:
                    # No size restriction, assume compatible
                    score += 0.15
                    weight_sum += 0.3

                # Schema compatibility (weight: 0.3)
                if characteristics.num_columns:
                    # Operations that work with tabular data
                    if hasattr(attrs, 'requires_columns') and attrs.requires_columns:
                        score += 0.3
                    else:
                        score += 0.15
                    weight_sum += 0.3

            # If no attributes, give neutral score
            if weight_sum == 0.0:
                return 0.5

            # Normalize score
            final_score = min(1.0, score / weight_sum)
            return final_score

        except Exception as e:
            self._logger.warning(f"Failed to score operation fit: {e}")
            return 0.3  # Default neutral-low score

    async def estimate_success_probability(
        self,
        operation: Type[BaseOperation],
        data: DataProfile
    ) -> float:
        """
        Estimates probability of successful execution.

        Args:
            operation: Operation type
            data: Data profile

        Returns:
            Success probability (0.0 to 1.0)
        """
        try:
            # Analyze the data profile
            characteristics = await self.analyze_data_profile(data)

            # Base probability on fit score
            fit_score = self.score_operation_fit(operation, characteristics)

            # Adjust based on data quality
            quality_factor = 1.0

            # Reduce probability if data has issues
            if characteristics.has_nulls:
                quality_factor *= 0.9  # 10% penalty for nulls

            # Reduce probability for very large datasets (higher risk)
            if characteristics.size_mb > 1000:  # > 1GB
                quality_factor *= 0.85

            # Reduce probability if data type is unknown
            if characteristics.data_type == 'unknown':
                quality_factor *= 0.7

            # Calculate final probability
            success_prob = fit_score * quality_factor

            # Ensure in valid range
            success_prob = max(0.0, min(1.0, success_prob))

            self._logger.debug(f"Estimated success probability: {success_prob:.2f}")
            return success_prob

        except Exception as e:
            self._logger.error(e, self.__class__.__name__)
            return 0.5  # Default neutral probability

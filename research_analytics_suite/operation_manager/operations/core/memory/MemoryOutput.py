"""
MemoryOutput Module

A class representing a collection of memory output slots for storing data produced by operations.

Author: Lane Copyright: Lane Credits: Lane License: BSD 3-Clause License Version: 0.0.0.1 Maintainer: Lane Email:
justlane@uw.edu Status: Prototype
"""

import numpy as np
from research_analytics_suite.data_engine.memory.MemorySlotCollection import MemorySlotCollection


class MemoryOutput(MemorySlotCollection):
    """
    A class representing a collection of memory output slots for storing data produced by operations.

    Methods:
        aggregate_results() -> dict: Aggregate results from all output slots.
        postprocess_data(): Postprocess all output data.
        validate_results(): Validate all output results.
    """
    def __init__(self, name):
        super().__init__(name=name)

    async def aggregate_results(self) -> dict:
        """Aggregate results from all output slots."""
        aggregated_results = dict()
        for slot in self.list_slots:
            aggregated_results.update(slot.data)
        return aggregated_results

    def postprocess_data(self):         # pragma: no cover
        """Postprocess all output data."""
        pass

    async def validate_results(self):   # pragma: no cover
        """Validate all output results."""
        pass

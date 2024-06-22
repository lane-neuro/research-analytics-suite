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
    def __init__(self):
        super().__init__()

    async def aggregate_results(self) -> dict:
        """Aggregate results from all output slots."""
        aggregated_results = dict()
        for slot in self.slots:
            aggregated_results.update(slot.data)
        return aggregated_results

    def postprocess_data(self):
        """Postprocess all output data."""
        for slot in self.slots:
            # Example postprocessing steps
            data = slot.data
            if 'values' in data:
                values = np.array(data['values'])
                # Scaling back to original range (assuming original range was 0-1)
                data['values'] = values * (values.max() - values.min()) + values.min()
                slot.data = data

    async def validate_results(self):
        """Validate all output results."""
        for slot in self.slots:
            data = slot.data
            if 'values' in data:
                values = np.array(data['values'])
                # Example validation: check if values are within a certain range
                # if not np.all((values >= 0) & (values <= 1)):
                #     raise ValueError(f"Output slot {slot.memory_id} contains values out of range [0, 1]")

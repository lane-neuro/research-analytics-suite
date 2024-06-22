"""
MemoryInput Module

A class representing a collection of memory input slots for storing data required by operations.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
from typing import List

import numpy as np
from research_analytics_suite.data_engine.memory.MemorySlotCollection import MemorySlotCollection


class MemoryInput(MemorySlotCollection):
    """
    A class representing a collection of memory input slots for storing data required by operations.

    Methods:
        validate_inputs(): Validate all input data.
        preprocess_data(): Preprocess all input data.
        add_dependency(memory_id: str, dependency_id: str): Add a dependency between input slots.
        remove_dependency(memory_id: str, dependency_id: str): Remove a dependency between input slots.
        list_dependencies(memory_id: str) -> List[str]: List all dependencies for a given input slot.
    """
    def __init__(self):
        super().__init__()
        self._dependencies = {}

    async def validate_inputs(self):
        """Validate all input data."""
        for slot in self.slots:
            if slot.operation_required and not slot.data:
                raise ValueError(f"Input slot {slot.memory_id} is required but has no data")

    async def preprocess_data(self):
        """Preprocess all input data."""
        for slot in self.slots:
            # Example preprocessing steps
            data = slot.data
            if 'values' in data:
                values = np.array(data['values'])
                # Normalization
                data['values'] = (values - values.min()) / (values.max() - values.min())
                # Cleaning
                data['values'] = np.nan_to_num(values)
                slot.data = data

    def add_dependency(self, memory_id: str, dependency_id: str):
        """Add a dependency between input slots."""
        if memory_id not in self._dependencies:
            self._dependencies[memory_id] = []
        self._dependencies[memory_id].append(dependency_id)

    def remove_dependency(self, memory_id: str, dependency_id: str):
        """Remove a dependency between input slots."""
        if memory_id in self._dependencies:
            self._dependencies[memory_id] = [d for d in self._dependencies[memory_id] if d != dependency_id]

    def list_dependencies(self, memory_id: str) -> List[str]:
        """List all dependencies for a given input slot."""
        return self._dependencies.get(memory_id, [])

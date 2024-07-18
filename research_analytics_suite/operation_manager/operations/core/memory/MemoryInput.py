from typing import List

import numpy as np
from research_analytics_suite.data_engine.memory.MemorySlotCollection import MemorySlotCollection
from research_analytics_suite.utils import CustomLogger


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
    def __init__(self, name):
        super().__init__(name=name)
        self._dependencies = {}

    async def validate_inputs(self) -> bool:
        """
        Validate all input data.

        Returns:
            bool: True if all input data is valid, False otherwise.
        """
        _output = True
        for slot in self.list_slots:
            if slot.operation_required and not slot.data:
                _output = False
                CustomLogger().error(ValueError(f"Input slot {slot.memory_id} is required but has no data"),
                                     self.__class__.__name__)
        return _output

    async def preprocess_data(self):
        ...
        # for slot in self.list_slots:
        #     data = slot.data
        #     if 'values' in data:
        #         values = np.array([v if v is not None else 0 for v in data['values'][1]])
        #         data['values'] = (
        #            values - values.min()) / (values.max() - values.min()) if values.max() != values.min() else values
        #         data['values'] = np.nan_to_num(data['values'][1])
        #         slot.data = {'values': list(data['values'][1])}

    def add_dependency(self, memory_id: str, dependency_id: str):
        if memory_id not in self._dependencies:
            self._dependencies[memory_id] = []
        self._dependencies[memory_id].append(dependency_id)

    def remove_dependency(self, memory_id: str, dependency_id: str):
        if memory_id in self._dependencies:
            self._dependencies[memory_id] = [d for d in self._dependencies[memory_id] if d != dependency_id]

    def list_dependencies(self, memory_id: str) -> List[str]:
        return self._dependencies.get(memory_id, [])

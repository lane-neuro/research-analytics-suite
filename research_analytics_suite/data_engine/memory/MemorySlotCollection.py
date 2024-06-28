"""
MemorySlotCollection Module

An abstract base class representing a collection of memory slots for storing data.

Author: Lane
"""
from abc import ABC
from typing import List, Optional
import json
import uuid

from .MemorySlot import MemorySlot


class MemorySlotCollection(ABC):
    """
    An abstract base class representing a collection of memory slots for storing data.

    Properties:
        collection_id (str): A unique identifier for the collection.
        name (str): A name for the collection.
        slots (List[MemorySlot]): A list of memory slots.

    Methods:
        add_slot(slot: MemorySlot): Add a memory slot to the collection.
        remove_slot(memory_id: str): Remove a memory slot from the collection by its ID.
        get_slot(memory_id: str) -> Optional[MemorySlot]: Retrieve a memory slot by its ID.
        list_slots() -> List[MemorySlot]: List all memory slots.
        clear_slots(): Clear all memory slots.
        update_slot(slot: MemorySlot): Update an existing memory slot.
        slot_exists(memory_id: str) -> bool: Check if a slot exists by its ID.
        to_dict() -> dict: Convert the collection to a dictionary.
        from_dict(data: dict): Initialize the collection from a dictionary.
        to_json() -> str: Convert the collection to a JSON string.
        from_json(data: str): Initialize the collection from a JSON string.
        filter_slots(operation_required: bool) -> List[MemorySlot]: Filter slots based on operation_required.
        find_slots_by_name(name: str) -> List[MemorySlot]: Find slots by name.
        add_slots(slots: List[MemorySlot]): Add multiple slots at once.
        remove_slots(memory_ids: List[str]): Remove multiple slots at once by their IDs.
    """
    def __init__(self, name: str = None):
        if name is None or name == "" or not isinstance(name, str):
            self._name = f"Collection - {uuid.uuid4().hex[:4]}"
        else:
            self._name = name

        self.collection_id = str(uuid.uuid4().hex)  # Generate a unique identifier for the collection
        self.slots: List[MemorySlot] = []

        from research_analytics_suite.data_engine import Workspace
        Workspace().add_memory_collection(self)

    @property
    def display_name(self) -> str:
        """Get the display name of the collection."""
        return f"{self.name} [{self.collection_id[:3]}]"

    @property
    def name(self) -> str:
        """Get the name of the collection."""
        return self._name

    @name.setter
    def name(self, value: str):
        """Set the name of the collection."""
        if not isinstance(value, str):
            raise ValueError("name must be a string")
        self._name = value

    def list_slots(self) -> Optional[list[MemorySlot]]:
        """List all memory slots."""
        if len(self.slots) > 0:
            return self.slots
        return None

    def add_slot(self, slot: MemorySlot):
        """Add a memory slot to the collection."""
        self.slots.append(slot)

    def new_slot_with_data(self, data: dict) -> MemorySlot:
        """Create a new memory slot from data and add it to the collection."""
        slot = MemorySlot(memory_id=str(uuid.uuid4()), data=data, operation_required=False, name="imported_data")

        self.add_slot(slot)
        return slot

    async def remove_slot(self, memory_id: str):
        """Remove a memory slot from the collection by its ID."""
        self.slots = [slot for slot in self.slots if slot.memory_id != memory_id]

    def get_slot(self, memory_id: str) -> Optional[MemorySlot]:
        """Retrieve a memory slot by its ID."""
        for slot in self.slots:
            if slot.memory_id == memory_id:
                return slot
        return None

    def get_slot_data(self, memory_id: str) -> Optional[dict]:
        """Retrieve the data of a memory slot by its ID."""
        slot = self.get_slot(memory_id)
        return slot.data if slot else None

    async def clear_slots(self):
        """Clear all memory slots."""
        self.slots.clear()

    async def update_slot(self, slot: MemorySlot):
        """Update an existing memory slot."""
        for i, s in enumerate(self.slots):
            if s.memory_id == slot.memory_id:
                self.slots[i] = slot
                return
        raise ValueError(f"No slot found with memory_id: {slot.memory_id}")

    async def slot_exists(self, memory_id: str) -> bool:
        """Check if a slot exists by its ID."""
        return any(slot.memory_id == memory_id for slot in self.slots)

    async def to_dict(self) -> dict:
        """Convert the collection to a dictionary."""
        return {
            'collection_id': self.collection_id,
            'name': self.name,
            'slots': [await slot.to_dict() for slot in self.slots]
        }

    @staticmethod
    async def from_dict(data: dict) -> 'MemorySlotCollection':
        """Initialize the collection from a dictionary."""
        _name = data.get('name', None)
        collection = MemorySlotCollection(name=_name)
        collection.collection_id = data.get('collection_id', str(uuid.uuid4()))
        for slot_data in data.get('slots', []):
            collection.add_slot(await MemorySlot.load_from_disk(slot_data))
        return collection

    def to_json(self) -> str:
        """Convert the collection to a JSON string."""
        return json.dumps(self.to_dict())

    @staticmethod
    async def from_json(data: str) -> 'MemorySlotCollection':
        """Initialize the collection from a JSON string."""
        return await MemorySlotCollection.from_dict(json.loads(data))

    def filter_slots(self, operation_required: bool) -> List[MemorySlot]:
        """Filter slots based on operation_required."""
        return [slot for slot in self.slots if slot.operation_required == operation_required]

    def find_slots_by_name(self, name: str) -> List[MemorySlot]:
        """Find slots by name."""
        return [slot for slot in self.slots if slot.name == name]

    def add_slots(self, slots: List[MemorySlot]):
        """Add multiple slots at once."""
        self.slots.extend(slots)

    def remove_slots(self, memory_ids: List[str]):
        """Remove multiple slots at once by their IDs."""
        self.slots = [slot for slot in self.slots if slot.memory_id not in memory_ids]

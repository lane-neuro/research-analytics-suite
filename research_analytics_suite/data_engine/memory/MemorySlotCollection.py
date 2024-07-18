"""
MemorySlotCollection Module

An abstract base class representing a collection of memory slots for storing data.

Author: Lane
"""
from __future__ import annotations
from abc import ABC
from typing import List, Optional
import json
import uuid

from research_analytics_suite.data_engine.memory.MemorySlot import MemorySlot
from research_analytics_suite.commands import command, link_class_commands
from research_analytics_suite.utils import CustomLogger


@link_class_commands
class MemorySlotCollection(ABC):
    """
    An abstract base class representing a collection of memory slots for storing data.

    Properties:
        collection_id (str): A unique identifier for the collection.
        name (str): A name for the collection.
        list_slots -> List[MemorySlot]: List all memory slots.

    Methods:
        add_slot(slot: MemorySlot): Add a memory slot to the collection.
        remove_slot(memory_id: str): Remove a memory slot from the collection by its ID.
        get_slot(memory_id: str) -> Optional[MemorySlot]: Retrieve a memory slot by its ID.
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
        """
        Initialize the collection with a name.

        Args:
            name (str): The name of the collection.
        """

        if name is None or name == "" or not isinstance(name, str):
            self._name = f"Collection - {uuid.uuid4().hex[:4]}"
        else:
            self._name = name

        self.collection_id = str(uuid.uuid4().hex)  # Generate a unique identifier for the collection
        self._slots: List[MemorySlot] = []

        from research_analytics_suite.data_engine import MemoryManager
        MemoryManager().add_collection(self)

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
            CustomLogger().error(ValueError("name must be a string"), self.__class__.__name__)
            return

        self._name = value

    @property
    @command
    def list_slots(self) -> list[MemorySlot]:
        """
        Returns all memory slots.

        Returns:
            list[MemorySlot]: List of all memory slots.
        """
        if isinstance(self._slots, list) and len(self._slots) > 0:
            return self._slots
        return []

    @command
    def add_slot(self, slot: MemorySlot):
        """
        Add a memory slot to the collection.

        Args:
            slot (MemorySlot): The memory slot to add.
        """
        if not isinstance(slot, MemorySlot):
            CustomLogger().error(ValueError("slot must be an instance of MemorySlot"), self.__class__.__name__)
            return

        if slot.memory_id in [s.memory_id for s in self._slots]:
            if slot.data != self.get_slot_data(slot.memory_id):
                self.update_slot(slot)
            return

        self._slots.append(slot)

    @command
    def new_slot_with_data(self, data: dict) -> MemorySlot:
        """
        Create a new memory slot from data and add it to the collection.

        Args:
            data (dict): The data to store in the memory slot.

        Returns:
            MemorySlot: The newly created memory slot.
        """
        slot = MemorySlot(memory_id=str(uuid.uuid4()), data=data, operation_required=False, name="imported_data")

        self.add_slot(slot)
        return slot

    @command
    async def remove_slot(self, memory_id: str):
        """
        Remove a memory slot from the collection by its ID.

        Args:
            memory_id (str): The ID of the memory slot to remove.
        """
        self._slots = [slot for slot in self._slots if slot.memory_id != memory_id]

    @command
    def get_slot(self, memory_id: str) -> Optional[MemorySlot]:
        """
        Retrieve a memory slot by its ID.

        Args:
            memory_id (str): The ID of the memory slot to retrieve.

        Returns:
            MemorySlot: The retrieved memory slot.
        """
        for slot in self._slots:
            if slot.memory_id == memory_id:
                return slot
        return None

    @command
    def get_slot_data(self, memory_id: str) -> Optional[dict]:
        """
        Retrieve the data of a memory slot by its ID.

        Args:
            memory_id (str): The ID of the memory slot to retrieve.

        Returns:
            dict: The data of the memory slot.
        """
        slot = self.get_slot(memory_id)
        return slot.data if slot else None

    @command
    async def clear_slots(self):
        """Clear all memory slots."""
        self._slots.clear()

    @command
    async def update_slot(self, slot: MemorySlot):
        """
        Update an existing memory slot.

        Args:
            slot (MemorySlot): The updated memory slot.
        """
        for i, s in enumerate(self.list_slots):
            if s.memory_id == slot.memory_id:
                self._slots[i] = slot
                return
        CustomLogger().error(ValueError(f"No slot found with memory_id: {slot.memory_id}"), self.__class__.__name__)

    @command
    async def slot_exists(self, memory_id: str) -> bool:
        """
        Check if a slot exists by its ID.

        Args:
            memory_id (str): The ID of the memory slot to check.

        Returns:
            bool: True if the slot exists, False otherwise.
        """
        return any(slot.memory_id == memory_id for slot in self.list_slots)

    async def to_dict(self) -> dict:
        """
        Convert the collection to a dictionary.

        Returns:
            dict: The collection as a dictionary.
        """
        return {
            'collection_id': self.collection_id,
            'name': self.name,
            'slots': [await slot.to_dict() for slot in self.list_slots]
        }

    @staticmethod
    @command
    async def from_dict(data: dict) -> MemorySlotCollection:
        """
        Initialize the collection from a dictionary.

        Args:
            data (dict): The dictionary to initialize the collection from.

        Returns:
            MemorySlotCollection: The initialized collection.
        """
        _name = data.get('name', None)
        collection = MemorySlotCollection(name=_name)
        collection.collection_id = data.get('collection_id', str(uuid.uuid4()))
        for slot_data in data.get('slots', []):
            collection.add_slot(await MemorySlot.load_from_disk(slot_data))
        return collection

    @command
    def to_json(self) -> str:
        """
        Convert the collection to a JSON string.

        Returns:
            str: The collection as a JSON string.
        """
        return json.dumps(self.to_dict(), indent=4)

    @staticmethod
    @command
    async def from_json(data: str) -> MemorySlotCollection:
        """
        Initialize the collection from a JSON string.

        Args:
            data (str): The JSON string to initialize the collection from.

        Returns:
            MemorySlotCollection: The initialized collection.
        """
        return await MemorySlotCollection.from_dict(json.loads(data))

    @command
    def filter_slots(self, operation_required: bool) -> List[MemorySlot]:
        """
        Filter slots based on operation_required.

        Args:
            operation_required (bool): The value to filter slots by.

        Returns:
            List[MemorySlot]: The filtered list of memory slots.
        """
        return [slot for slot in self._slots if slot.operation_required == operation_required]

    @command
    def find_slots_by_name(self, name: str) -> List[MemorySlot]:
        """
        Find slots by name.

        Args:
            name (str): The name to search for.

        Returns:
            List[MemorySlot]: The list of memory slots with the specified name.
        """
        return [slot for slot in self._slots if slot.name == name]

    @command
    def add_slots(self, slots: List[MemorySlot]):
        """
        Add multiple slots at once.

        Args:
            slots (List[MemorySlot]): The slots to add.
        """
        for slot in slots:
            self.add_slot(slot)

    @command
    def remove_slots(self, memory_ids: List[str]):
        """
        Remove multiple slots at once by their IDs.

        Args:
            memory_ids (List[str]): The IDs of the slots to remove.
        """
        self._slots = [slot for slot in self._slots if slot.memory_id not in memory_ids]

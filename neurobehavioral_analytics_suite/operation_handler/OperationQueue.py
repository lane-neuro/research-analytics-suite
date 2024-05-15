from collections import deque

from neurobehavioral_analytics_suite.operation_handler.Operation import Operation
from neurobehavioral_analytics_suite.operation_handler.OperationLinkedList import OperationLinkedList
from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler


class OperationQueue:
    def __init__(self, error_handler: ErrorHandler = ErrorHandler()):
        self.queue = deque()
        self.error_handler = error_handler

    async def add_operation(self, operation) -> None:
        if isinstance(operation, Operation):
            operation = OperationLinkedList(operation)
        self.queue.append(operation)

    async def remove_operation(self, operation) -> None:
        if isinstance(operation, Operation):
            operation = next((op for op in self.queue if op.head.operation == operation), None)
        if operation:
            self.queue.remove(operation)

    def get_operation(self, operation_list: OperationLinkedList) -> Operation:
        return operation_list.head.operation

    def get_operation_by_task(self, task) -> Operation:
        for operation_list in self.queue:
            if self.get_operation(operation_list).task == task:
                return self.get_operation(operation_list)

    def insert_operation(self, index, operation) -> None:
        if isinstance(operation, Operation):
            operation = OperationLinkedList(operation)
        self.queue.insert(index, operation)

    def is_empty(self) -> bool:
        return len(self.queue) == 0

    def size(self) -> int:
        return len(self.queue)

    def clear(self) -> None:
        self.queue.clear()

    def contains(self, operation) -> bool:
        return any(op.head.operation == operation for op in self.queue)

    def has_pending_operations(self) -> bool:
        return any(op.head.operation.status == "pending" for op in self.queue)

    async def execute_operations(self):
        while not self.is_empty():
            operation_list = self.dequeue()
            await operation_list.execute_operations()
            await self.remove_operation(operation_list)

    def dequeue(self):
        if self.is_empty():
            return None
        return self.queue.popleft()

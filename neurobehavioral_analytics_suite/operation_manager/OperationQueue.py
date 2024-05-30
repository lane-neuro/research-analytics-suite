from collections import deque
from neurobehavioral_analytics_suite.operation_manager.operation.Operation import Operation
from neurobehavioral_analytics_suite.operation_manager.OperationChain import OperationChain


class OperationQueue:
    def __init__(self, logger, error_handler):
        self.queue = deque()
        self.logger = logger
        self.error_handler = error_handler

    async def add_operation_to_queue(self, operation) -> None:
        if not isinstance(operation, OperationChain):
            operation = OperationChain(operation)
        self.queue.append(operation)

    def remove_operation_from_queue(self, operation):
        if isinstance(operation, OperationChain):
            self.queue.remove(operation)
        elif isinstance(operation, Operation):
            operation_chain = next((op for op in self.queue if op.head.operation == operation), None)
            if operation_chain:
                operation_chain.remove_operation(operation)
                if operation_chain.is_empty():
                    self.queue.remove(operation_chain)

    def get_operation_from_chain(self, operation_chain: OperationChain) -> Operation:
        if isinstance(operation_chain, OperationChain):
            return operation_chain.head.operation

    def get_operation_by_task(self, task) -> Operation:
        for operation_chain in self.queue:
            operation = self.get_operation_from_chain(operation_chain)
            if operation:
                if operation.task == task:
                    return operation
            else:
                self.logger.error(f"No operation found for operation chain {operation_chain}")

    def insert_operation(self, index, operation) -> None:
        if isinstance(operation, OperationChain):
            self.queue.insert(index, operation)
        elif isinstance(operation, Operation):
            operation = OperationChain(operation)
            self.queue.insert(index, operation)

    def is_empty(self) -> bool:
        return len(self.queue) == 0

    def size(self) -> int:
        return len(self.queue)

    def clear(self) -> None:
        self.queue.clear()

    def contains(self, operation) -> bool:
        if isinstance(operation, OperationChain):
            return operation in self.queue
        elif isinstance(operation, Operation):
            return any(op.head.operation == operation for op in self.queue)

    async def has_pending_operations(self) -> bool:
        return any(await self.get_operation_from_chain(op).status == "pending" for op in self.queue)

    async def dequeue(self):
        if self.is_empty():
            return None
        return self.queue.popleft()

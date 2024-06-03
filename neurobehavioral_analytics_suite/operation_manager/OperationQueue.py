from collections import deque
from neurobehavioral_analytics_suite.operation_manager.operations.Operation import Operation
from neurobehavioral_analytics_suite.operation_manager.OperationChain import OperationChain


class OperationQueue:
    def __init__(self, logger, error_handler):
        self.queue = deque()
        self.logger = logger
        self.error_handler = error_handler

    async def add_operation_to_queue(self, operation) -> Operation:
        if operation.parent_operation is None:
            if not isinstance(operation, OperationChain):
                operation = OperationChain(operation)
            self.queue.append(operation)
        else:
            op_head = self.get_chain_by_operation(operation.parent_operation)
            if op_head:
                op_head.add_operation_to_chain(operation)

        return self.get_operation_in_chain(self.get_chain_by_operation(operation), operation)

    def insert_operation_in_chain(self, index, operation_chain, operation) -> None:
        if isinstance(operation_chain, OperationChain):
            current_node = operation_chain.head
            for i in range(index):
                if current_node:
                    current_node = current_node.next_node
            if current_node:
                current_node.operation = operation

    def remove_operation_from_chain(self, operation_chain, operation) -> None:
        if isinstance(operation_chain, OperationChain):
            operation_chain.remove_operation(operation)
            if operation_chain.is_empty():
                self.queue.remove(operation_chain)

    def move_operation(self, operation, new_index) -> None:
        operation_chain = self.get_chain_by_operation(operation)
        if operation_chain:
            operation_chain.remove_operation(operation)
            self.insert_operation_in_chain(new_index, operation_chain, operation)

    def remove_operation_from_queue(self, operation):
        if isinstance(operation, OperationChain):
            self.queue.remove(operation)
        elif isinstance(operation, Operation):
            operation_chain = next((op for op in self.queue if op.head.operation == operation), None)
            if operation_chain:
                operation_chain.remove_operation(operation)
                if operation_chain.is_empty():
                    self.queue.remove(operation_chain)

    def get_head_operation_from_chain(self, operation_chain: OperationChain) -> Operation:
        if isinstance(operation_chain, OperationChain):
            return operation_chain.head.operation

    def get_chain_by_operation(self, operation) -> OperationChain:
        return next((op for op in self.queue if op.head.operation == operation), None)

    def get_operation_in_chain(self, operation_chain: OperationChain, operation) -> Operation:
        if isinstance(operation_chain, OperationChain):
            current_node = operation_chain.head
            while current_node:
                if current_node.operation == operation:
                    return current_node.operation
                current_node = current_node.next_node

    def get_operation_by_type(self, operation_type) -> Operation:
        for operation_chain in self.queue:
            for node in operation_chain:
                if isinstance(node.operation, operation_type):
                    return node.operation
        self.logger.error(f"No operation found of type {operation_type.__name__}")

    def find_operation_by_task(self, task) -> Operation:
        for operation_chain in self.queue:
            for node in operation_chain:
                if node.operation.task == task:
                    return node.operation
        self.logger.error(f"No operation found for task {task}")

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

    async def has_waiting_operations(self) -> bool:
        return any(await self.get_head_operation_from_chain(op).status == "waiting" for op in self.queue)

    async def dequeue(self):
        if self.is_empty():
            return None
        return self.queue.popleft()

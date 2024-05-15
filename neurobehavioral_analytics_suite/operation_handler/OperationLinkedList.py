from neurobehavioral_analytics_suite.operation_handler.Operation import Operation


class OperationNode:
    def __init__(self, operation: Operation, next_node=None):
        self.operation = operation
        self.next_node = next_node


class OperationLinkedList:
    def __init__(self, operation: Operation = None):
        self.head = None
        if isinstance(operation, Operation):
            self.add_operation(operation)

    def add_operation(self, operation: Operation):
        if not self.head:
            self.head = OperationNode(operation)
        else:
            current_node = self.head
            while current_node.next_node:
                current_node = current_node.next_node
            current_node.next_node = OperationNode(operation)

    def remove_operation(self, operation: Operation):
        if self.head and self.head.operation == operation:
            self.head = self.head.next_node
        else:
            current_node = self.head
            while current_node and current_node.next_node:
                if current_node.next_node.operation == operation:
                    current_node.next_node = current_node.next_node.next_node
                    break
                current_node = current_node.next_node

    async def execute_operations(self):
        current_node = self.head
        while current_node:
            await current_node.operation.execute()
            current_node = current_node.next_node

    def __iter__(self):
        current_node = self.head
        while current_node:
            yield current_node
            current_node = current_node.next_node
            
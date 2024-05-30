from neurobehavioral_analytics_suite.operation_manager.operations.persistent.ConsoleOperation import ConsoleOperation
from neurobehavioral_analytics_suite.operation_manager.operations.CustomOperation import CustomOperation
from neurobehavioral_analytics_suite.operation_manager.operations.Operation import Operation
from neurobehavioral_analytics_suite.operation_manager.operations.persistent.ResourceMonitorOperation import \
    ResourceMonitorOperation


class OperationNode:
    def __init__(self, operation: Operation, next_node=None):
        self.operation = operation
        self.next_node = next_node


class OperationChain:
    def __init__(self, operation: Operation = None):
        self.head = None
        if (isinstance(operation, Operation) or
                isinstance(operation, CustomOperation) or
                isinstance(operation, ResourceMonitorOperation) or
                isinstance(operation, ConsoleOperation)):
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

    def is_empty(self):
        return not self.head

    def count_operations(self):
        count = 0
        current_node = self.head
        while current_node:
            count += 1
            current_node = current_node.next_node
        return count

    def __iter__(self):
        current_node = self.head
        while current_node:
            yield current_node
            current_node = current_node.next_node
            
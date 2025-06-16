"""
Operation:      MongoDBOperations
Version:        0.0.1
Description:    Perform CRUD operations on a MongoDB database.

Author:         Lane
GitHub:         lane-neuro
Email:          justlane@uw.edu

---
Part of the Research Analytics Suite
    https://github.com/lane-neuro/research-analytics-suite
License:        BSD 3-Clause License
Maintainer:     Lane (GitHub: @lane-neuro)
Status:         In Progress
"""
from typing import Optional, Type
from pymongo import MongoClient
from research_analytics_suite.operation_manager import BaseOperation


class MongoDBOperations(BaseOperation):
    """
    Perform CRUD operations on a MongoDB database.

    Requires:
        connection_string (str): The MongoDB connection string.
        database_name (str): The name of the MongoDB database.
        collection_name (str): The name of the MongoDB collection.

    Returns:
        client: The MongoDB client.
        database: The MongoDB database.
        collection: The MongoDB collection
        documents: The documents in the MongoDB collection.
    """
    name = "MongoDBOperations"
    version = "0.0.1"
    description = "Perform CRUD operations on a MongoDB database."
    category_id = 702
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    required_inputs = {"connection_string": str, "database_name": str, "collection_name": str}
    parent_operation: Optional[Type[BaseOperation]] = None
    inheritance: Optional[list] = []
    is_loop = False
    is_cpu_bound = False
    parallel = False

    def __init__(self, *args, **kwargs):
        """
        Initialize the operation.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)

    async def initialize_operation(self):
        """
        Initialize any resources or setup required for the operation before it starts.
        """
        await super().initialize_operation()

    async def execute(self):
        """
        Execute the operation's logic: perform CRUD operations on the MongoDB database.
        """
        _inputs = self.get_inputs()
        connection_string = _inputs.get("connection_string", "")
        database_name = _inputs.get("database_name", "")
        collection_name = _inputs.get("collection_name", "")

        client = MongoClient(connection_string)
        database = client[database_name]
        collection = database[collection_name]

        documents = list(collection.find())
        return {
            "client": client,
            "database": database,
            "collection": collection,
            "documents": documents
        }

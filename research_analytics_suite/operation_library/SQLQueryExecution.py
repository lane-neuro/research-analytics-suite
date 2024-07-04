"""
Operation:      SQLQueryExecution
Version:        0.0.1
Description:    Execute SQL queries on a database.

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
import sqlite3
from research_analytics_suite.operation_manager import BaseOperation


class SQLQueryExecution(BaseOperation):
    """
    Execute SQL queries on a database.

    Attributes:
        database (str): The path to the SQLite database file.
        query (str): The SQL query to execute.

    Returns:
        connection: The connection to the SQLite database.
        cursor: The cursor for the database connection.
        results: The results of the query.
    """
    name = "SQLQueryExecution"
    version = "0.0.1"
    description = "Execute SQL queries on a database."
    category_id = 701
    author = "Lane"
    github = "lane-neuro"
    email = "justlane@uw.edu"
    unique_id = f"{github}_{name}_{version}"
    required_inputs = {"database": str, "query": str}
    parent_operation: Optional[Type[BaseOperation]] = None
    inheritance: Optional[list] = []
    is_loop = False
    is_cpu_bound = False
    parallel = False

    def __init__(self, database: str, query: str, *args, **kwargs):
        """
        Initialize the operation with the database and query.

        Args:
            database (str): The path to the SQLite database file.
            query (str): The SQL query to execute.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self.database = database
        self.query = query
        super().__init__(*args, **kwargs)

    async def initialize_operation(self):
        """
        Initialize any resources or setup required for the operation before it starts.
        """
        await super().initialize_operation()

    async def execute(self):
        """
        Execute the operation's logic: execute the SQL query on the database.
        """
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()
        cursor.execute(self.query)
        results = cursor.fetchall()
        connection.close()
        print(f"Query Results: {results}")

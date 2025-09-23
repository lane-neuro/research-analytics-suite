"""
CommandExporter Module

This module defines the CommandExporter class, which exports registered commands to various formats
including SQLite database, JSON, and CSV for documentation generation and analysis.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import json
import sqlite3
import csv
import os
from datetime import datetime
from typing import Dict, Any, List


class CommandExporter:
    """Class to export command registry data to various formats."""

    def __init__(self, registry: Dict[str, Any]):
        """
        Initialize the CommandExporter with a command registry.

        Args:
            registry: The command registry dictionary to export.
        """
        self.registry = registry
        self._logger = None
        self._config = None

    async def initialize(self):
        """Initialize logger and config dependencies."""
        try:
            from research_analytics_suite.utils import CustomLogger
            self._logger = CustomLogger()

            from research_analytics_suite.utils import Config
            self._config = Config()
        except Exception as e:
            print(f"Failed to initialize CommandExporter: {e}")

    def _serialize_command_data(self, command_name: str, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Serialize command data for export, handling non-serializable objects.

        Args:
            command_name: Name of the command
            command_data: Command metadata dictionary

        Returns:
            Serialized command data dictionary
        """
        def serialize_type(type_obj):
            """Convert type objects to string representation."""
            if hasattr(type_obj, '__name__'):
                return type_obj.__name__
            elif hasattr(type_obj, '__origin__'):
                return str(type_obj)
            else:
                return str(type_obj)

        def serialize_args(args_list):
            """Serialize argument list."""
            serialized_args = []
            for arg in args_list:
                serialized_arg = {
                    'name': arg.get('name', ''),
                    'type': serialize_type(arg.get('type', 'any')),
                    'required': True  # Default assumption
                }
                serialized_args.append(serialized_arg)
            return serialized_args

        # Extract basic command information
        serialized_data = {
            'name': command_name,
            'description': command_data.get('description', ''),
            'class_name': command_data.get('class_name', ''),
            'category': command_data.get('category', 'Uncategorized'),
            'tags': command_data.get('tags', []),
            'is_method': command_data.get('is_method', False),
            'args': serialize_args(command_data.get('args', [])),
            'return_type': self._serialize_return_type(command_data.get('return_type', [])),
            'instance_count': len(command_data.get('instances', {})),
            'module': getattr(command_data.get('func'), '__module__', '') if command_data.get('func') else '',
            'file_path': getattr(command_data.get('func'), '__code__', {}).co_filename if command_data.get('func') else '',
            'line_number': getattr(command_data.get('func'), '__code__', {}).co_firstlineno if command_data.get('func') else 0,
            'export_timestamp': datetime.now().isoformat()
        }

        return serialized_data

    def _serialize_return_type(self, return_type):
        """
        Serialize return type, handling both single types and lists of types.

        Args:
            return_type: The return type(s) to serialize

        Returns:
            List of serialized return type strings
        """
        def serialize_type(type_obj):
            """Convert type objects to string representation."""
            if type_obj is None:
                return 'None'
            elif hasattr(type_obj, '__name__'):
                return type_obj.__name__
            elif hasattr(type_obj, '__origin__'):
                return str(type_obj)
            else:
                return str(type_obj)

        if return_type is None:
            return ['None']
        elif isinstance(return_type, list):
            return [serialize_type(rt) for rt in return_type]
        else:
            # Single type object
            return [serialize_type(return_type)]

    async def export_to_sqlite(self, output_path: str = None) -> str:
        """
        Export command registry to SQLite database.

        Args:
            output_path: Optional path for the output file. If None, uses default location.

        Returns:
            Path to the created database file
        """
        if not output_path:
            if self._config:
                base_dir = getattr(self._config, 'BASE_DIR', os.getcwd())
                workspace_name = getattr(self._config, 'WORKSPACE_NAME', 'default')
                output_dir = os.path.join(base_dir, 'workspaces', workspace_name, 'documentation')
            else:
                output_dir = os.path.join(os.getcwd(), 'documentation')

            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, 'commands_registry.db')

        try:
            # Ensure the directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir:  # Only create directory if there is a directory part
                os.makedirs(output_dir, exist_ok=True)

            # Create database and tables
            conn = sqlite3.connect(output_path)
            cursor = conn.cursor()

            # Drop existing tables if they exist
            cursor.execute("DROP TABLE IF EXISTS commands")
            cursor.execute("DROP TABLE IF EXISTS command_args")
            cursor.execute("DROP TABLE IF EXISTS command_tags")

            # Create commands table
            cursor.execute("""
                CREATE TABLE commands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    class_name TEXT,
                    category TEXT,
                    is_method BOOLEAN,
                    return_type TEXT,
                    instance_count INTEGER,
                    module TEXT,
                    file_path TEXT,
                    line_number INTEGER,
                    export_timestamp TEXT
                )
            """)

            # Create command arguments table
            cursor.execute("""
                CREATE TABLE command_args (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command_name TEXT,
                    arg_name TEXT,
                    arg_type TEXT,
                    required BOOLEAN,
                    FOREIGN KEY (command_name) REFERENCES commands (name)
                )
            """)

            # Create command tags table
            cursor.execute("""
                CREATE TABLE command_tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command_name TEXT,
                    tag TEXT,
                    FOREIGN KEY (command_name) REFERENCES commands (name)
                )
            """)

            # Insert command data
            for command_name, command_data in self.registry.items():
                serialized_data = self._serialize_command_data(command_name, command_data)

                # Insert main command data
                cursor.execute("""
                    INSERT INTO commands (
                        name, description, class_name, category, is_method,
                        return_type, instance_count, module, file_path,
                        line_number, export_timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    serialized_data['name'],
                    serialized_data['description'],
                    serialized_data['class_name'],
                    serialized_data['category'],
                    serialized_data['is_method'],
                    ', '.join(serialized_data['return_type']),
                    serialized_data['instance_count'],
                    serialized_data['module'],
                    serialized_data['file_path'],
                    serialized_data['line_number'],
                    serialized_data['export_timestamp']
                ))

                # Insert arguments
                for arg in serialized_data['args']:
                    cursor.execute("""
                        INSERT INTO command_args (command_name, arg_name, arg_type, required)
                        VALUES (?, ?, ?, ?)
                    """, (command_name, arg['name'], arg['type'], arg['required']))

                # Insert tags
                for tag in serialized_data['tags']:
                    cursor.execute("""
                        INSERT INTO command_tags (command_name, tag)
                        VALUES (?, ?)
                    """, (command_name, tag))

            # Create useful views
            cursor.execute("""
                CREATE VIEW command_summary AS
                SELECT
                    c.name,
                    c.description,
                    c.class_name,
                    c.category,
                    c.is_method,
                    c.return_type,
                    c.instance_count,
                    GROUP_CONCAT(ca.arg_name || ':' || ca.arg_type, ', ') as arguments,
                    GROUP_CONCAT(ct.tag, ', ') as tags
                FROM commands c
                LEFT JOIN command_args ca ON c.name = ca.command_name
                LEFT JOIN command_tags ct ON c.name = ct.command_name
                GROUP BY c.name
            """)

            cursor.execute("""
                CREATE VIEW commands_by_category AS
                SELECT
                    category,
                    COUNT(*) as command_count,
                    GROUP_CONCAT(name, ', ') as commands
                FROM commands
                GROUP BY category
                ORDER BY command_count DESC
            """)

            conn.commit()
            conn.close()

            if self._logger:
                self._logger.info(f"Command registry exported to SQLite database: {output_path}")

            return output_path

        except Exception as e:
            if self._logger:
                self._logger.error(e, "CommandExporter.export_to_sqlite")
            else:
                print(f"Error exporting to SQLite: {e}")
            raise

    async def export_to_json(self, output_path: str = None) -> str:
        """
        Export command registry to JSON file.

        Args:
            output_path: Optional path for the output file. If None, uses default location.

        Returns:
            Path to the created JSON file
        """
        if not output_path:
            if self._config:
                base_dir = getattr(self._config, 'BASE_DIR', os.getcwd())
                workspace_name = getattr(self._config, 'WORKSPACE_NAME', 'default')
                output_dir = os.path.join(base_dir, 'workspaces', workspace_name, 'documentation')
            else:
                output_dir = os.path.join(os.getcwd(), 'documentation')

            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, 'commands_registry.json')

        try:
            # Ensure the directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir:  # Only create directory if there is a directory part
                os.makedirs(output_dir, exist_ok=True)

            # Serialize all command data
            serialized_registry = {}
            for command_name, command_data in self.registry.items():
                serialized_registry[command_name] = self._serialize_command_data(command_name, command_data)

            # Export metadata
            export_metadata = {
                'export_timestamp': datetime.now().isoformat(),
                'total_commands': len(self.registry),
                'commands': serialized_registry
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_metadata, f, indent=2, ensure_ascii=False)

            if self._logger:
                self._logger.info(f"Command registry exported to JSON: {output_path}")

            return output_path

        except Exception as e:
            if self._logger:
                self._logger.error(e, "CommandExporter.export_to_json")
            else:
                print(f"Error exporting to JSON: {e}")
            raise

    async def export_to_csv(self, output_path: str = None) -> str:
        """
        Export command registry to CSV file.

        Args:
            output_path: Optional path for the output file. If None, uses default location.

        Returns:
            Path to the created CSV file
        """
        if not output_path:
            if self._config:
                base_dir = getattr(self._config, 'BASE_DIR', os.getcwd())
                workspace_name = getattr(self._config, 'WORKSPACE_NAME', 'default')
                output_dir = os.path.join(base_dir, 'workspaces', workspace_name, 'documentation')
            else:
                output_dir = os.path.join(os.getcwd(), 'documentation')

            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, 'commands_registry.csv')

        try:
            # Ensure the directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir:  # Only create directory if there is a directory part
                os.makedirs(output_dir, exist_ok=True)

            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'name', 'description', 'class_name', 'category', 'is_method',
                    'return_type', 'arguments', 'tags', 'instance_count', 'module',
                    'file_path', 'line_number'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for command_name, command_data in self.registry.items():
                    serialized_data = self._serialize_command_data(command_name, command_data)

                    # Format data for CSV
                    csv_row = {
                        'name': serialized_data['name'],
                        'description': serialized_data['description'],
                        'class_name': serialized_data['class_name'],
                        'category': serialized_data['category'],
                        'is_method': serialized_data['is_method'],
                        'return_type': ', '.join(serialized_data['return_type']),
                        'arguments': ', '.join([f"{arg['name']}:{arg['type']}" for arg in serialized_data['args']]),
                        'tags': ', '.join(serialized_data['tags']),
                        'instance_count': serialized_data['instance_count'],
                        'module': serialized_data['module'],
                        'file_path': serialized_data['file_path'],
                        'line_number': serialized_data['line_number']
                    }
                    writer.writerow(csv_row)

            if self._logger:
                self._logger.info(f"Command registry exported to CSV: {output_path}")

            return output_path

        except Exception as e:
            if self._logger:
                self._logger.error(e, "CommandExporter.export_to_csv")
            else:
                print(f"Error exporting to CSV: {e}")
            raise

    async def export_all_formats(self, base_path: str = None) -> Dict[str, str]:
        """
        Export command registry to all supported formats.

        Args:
            base_path: Base directory for exports. If None, uses default location.

        Returns:
            Dictionary mapping format names to file paths
        """
        results = {}

        if base_path:
            sqlite_path = os.path.join(base_path, 'commands_registry.db')
            json_path = os.path.join(base_path, 'commands_registry.json')
            csv_path = os.path.join(base_path, 'commands_registry.csv')
        else:
            sqlite_path = json_path = csv_path = None

        try:
            results['sqlite'] = await self.export_to_sqlite(sqlite_path)
            results['json'] = await self.export_to_json(json_path)
            results['csv'] = await self.export_to_csv(csv_path)

            if self._logger:
                self._logger.info(f"Command registry exported to all formats: {results}")

            return results

        except Exception as e:
            if self._logger:
                self._logger.error(e, "CommandExporter.export_all_formats")
            else:
                print(f"Error exporting to all formats: {e}")
            raise
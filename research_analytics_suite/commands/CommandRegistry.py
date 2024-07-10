import inspect
from typing import get_type_hints, Optional

class CommandRegistry:
    """
    A class to manage the registration and discovery of commands.

    This class provides methods to register commands and discover them dynamically in a given package.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CommandRegistry, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._registry = {}
            self._instances = {}  # Dictionary to hold instances by runtime ID
            self._logger = None
            self._config = None
            self._operation_control = None
            self._library_manifest = None
            self._workspace = None

            self._initialized = False

    async def initialize(self):
        """
        Initializes the command registry with the necessary components.
        """
        if not self._initialized:
            from research_analytics_suite.utils import CustomLogger
            self._logger = CustomLogger()

            from research_analytics_suite.utils import Config
            self._config = Config()

            from research_analytics_suite.operation_manager.control.OperationControl import OperationControl
            self._operation_control = OperationControl()

            from research_analytics_suite.library_manifest import LibraryManifest
            self._library_manifest = LibraryManifest()

            from research_analytics_suite.data_engine import Workspace
            self._workspace = Workspace()

            self._initialize_collected_commands()

            self._initialized = True

    def _initialize_collected_commands(self):
        """
        Register all collected commands from the temporary registry after initialization.
        """
        global temp_command_registry
        for cmd_meta in temp_command_registry:
            self._initialize_command(cmd_meta)
        temp_command_registry = []  # Clear the temporary registry

    def _initialize_command(self, cmd_meta):
        """
        Initializes a command function with the given metadata.

        Args:
            cmd_meta (dict): The command metadata to register.
        """
        self._registry[cmd_meta['name']] = {
            'func': cmd_meta['func'],
            'name': cmd_meta['name'],
            'args': cmd_meta['args'],
            'return_type': cmd_meta['return_type'],
            'is_method': cmd_meta.get('is_method', False),  # Ensure 'is_method' is always included
            '_is_command': True
        }

    def discover_commands(self, package):
        """
        Discover and register all commands in the specified package.

        Args:
            package (str): The package name to discover commands in.
        """
        import importlib
        import pkgutil

        package = importlib.import_module(package)
        for loader, name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + '.'):
            module = importlib.import_module(name)
            for name, obj in inspect.getmembers(module):
                if inspect.isfunction(obj) and hasattr(obj, '_is_command'):
                    self._initialize_command({
                        'func': obj,
                        'name': obj.__name__,
                        'args': [{'name': param, 'type': get_type_hints(obj).get(param, str)} for param in
                                 inspect.signature(obj).parameters],
                        'return_type': get_type_hints(obj).get('return', None),
                        'is_method': False
                    })
                elif inspect.isclass(obj):
                    for method_name, method in inspect.getmembers(obj, predicate=inspect.isfunction):
                        if hasattr(method, '_is_command'):
                            self._initialize_command({
                                'func': method,
                                'name': f"{obj.__name__}.{method.__name__}",
                                'args': [{'name': param, 'type': get_type_hints(method).get(param, str)} for param in
                                         inspect.signature(method).parameters if param != 'self'],
                                'return_type': get_type_hints(method).get('return', None),
                                'is_method': True,
                                'class': obj  # Include the class context for methods
                            })

    def register_instance(self, instance, runtime_id):
        """
        Register an instance with a runtime ID.

        Args:
            instance: The instance to register.
            runtime_id: The runtime ID associated with the instance.
        """
        self._instances[runtime_id] = instance

    def execute_command(self, name, runtime_id=None, *args, **kwargs):
        """
        Execute a registered command.

        Args:
            name (str): The name of the command to execute.
            runtime_id: The runtime ID for instance-specific methods.
            *args: Positional arguments for the command.
            **kwargs: Keyword arguments for the command.

        Returns:
            The result of the command execution.
        """
        cmd_meta = self._registry.get(name)
        if cmd_meta is None:
            raise ValueError(f"Command '{name}' not found in the registry.")

        if cmd_meta['is_method'] and runtime_id is not None:
            instance = self._instances.get(runtime_id)
            if instance is None:
                raise ValueError(f"Instance with runtime ID '{runtime_id}' not found.")
            return cmd_meta['func'](instance, *args, **kwargs)
        else:
            return cmd_meta['func'](*args, **kwargs)

    @property
    def registry(self):
        """Returns the command registry."""
        return self._registry


temp_command_registry = []


def command(func=None):
    """
    Decorator to register a command.

    This decorator auto-detects the command name, argument names, types, and return type.
    """
    def wrapper(f):
        # Auto-detect arguments and return type
        sig = inspect.signature(f)
        try:
            type_hints = get_type_hints(f)
        except NameError as e:
            raise TypeError(f"Invalid type hint in function {f.__name__}: {e}")

        args = [{'name': param, 'type': type_hints.get(param, str)} for param in sig.parameters if param != 'self']
        return_type = type_hints.get('return', None)

        # Check if the function is already registered to prevent duplicates
        if not any(cmd_meta['func'] == f for cmd_meta in temp_command_registry):
            temp_command_registry.append({
                'func': f,
                'name': f.__name__,
                'args': args,
                'return_type': return_type,
                'is_method': 'self' in sig.parameters
            })

        f._is_command = True
        return f

    if func is None:
        return wrapper
    else:
        return wrapper(func)


def register_commands(cls):
    """
    Decorator to register all commands in a class.

    This decorator auto-detects all command methods in a class and registers them.
    """
    class_name = cls.__name__
    for method_name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        if hasattr(method, '_is_command'):
            sig = inspect.signature(method)
            type_hints = get_type_hints(method)
            args = [{'name': param, 'type': type_hints.get(param, str)} for param in sig.parameters if param != 'self']
            return_type = type_hints.get('return', None)

            # Check if the method is already registered to prevent duplicates
            if not any(cmd_meta['func'] == method for cmd_meta in temp_command_registry):
                temp_command_registry.append({
                    'func': method,
                    'name': f"{class_name}.{method.__name__}",
                    'args': args,
                    'return_type': return_type,
                    'is_method': True
                })
            else:
                for cmd_meta in temp_command_registry:
                    if cmd_meta['func'] == method:
                        cmd_meta['name'] = f"{class_name}.{method.__name__}"
    return cls

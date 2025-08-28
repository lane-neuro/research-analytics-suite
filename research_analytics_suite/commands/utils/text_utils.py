"""
Wrap text to the specified width.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
from __future__ import annotations

import inspect
import ast
import re
import textwrap
from collections import Counter
from pathlib import Path

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

from research_analytics_suite.utils import CustomLogger
from research_analytics_suite.utils.Resources import resource_path

CUSTOM_STOP_WORDS = {"the", "a", "an", "and", "or", "but", "if", "then", "else", "when", "where", "why", "how", "all",
                     "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only",
                     "own", "same", "so", "than", "too", "very", "can", "will", "just", "should", "now"}

VALID_WORDS = {"name", "description", "command", "operation", "data", "value", "input", "output", "file", "save",
               "load", "get", "set", "add", "remove", "update", "clear", "library", "category", "tag", "tags",
               "registry", "register", "unregister", "list", "show", "hide", "open", "close", "create", "delete",
               "destroy", "start", "stop", "pause", "resume", "run", "execute", "process", "analyze", "validate",
               "check", "verify", "monitor", "control", "manage", "configure", "setup", "initialize", "finalize",
               "shutdown", "restart", "refresh", "reset", "cancel", "abort", "exit", "quit", "help", "about", "version",
               "license", "author", "maintainer", "email", "status", "prototype", "development", "production",
               "testing", "debugging", "logging", "reporting", "messaging", "messaging", "notification", "alert",
               "warning", "error", "exception", "failure", "success", "progress", "task", "operation", "process",
               "function", "method", "class", "module", "package", "library", "framework", "system", "service",
               "component", "info", "error", "warning", "debug", "critical", "exception"}


def get_function_body(func):
    """
    Return just the body of a function/method as source.
    Works in dev (inspect) and frozen (reads bundled source).
    """
    # 1) Dev path
    try:
        src = inspect.getsource(func)
        return _extract_body_from_source(src)
    except (OSError, TypeError):
        pass

    # 2) Frozen fallback: read bundled source file
    mod_name = getattr(func, "__module__", None)
    fn_name  = getattr(func, "__name__", None)
    if not mod_name or not fn_name:
        return " "

    py_filename = mod_name.rsplit(".", 1)[-1] + ".py"
    src_path = resource_path(f"./operation_library_src/{py_filename}")

    try:
        text = Path(src_path).read_text(encoding="utf-8", errors="ignore")
        return _extract_body_from_module_text(text, fn_name)
    except Exception as e:
        CustomLogger().error(e, "get_function_body fallback failed")
        return " "

def _extract_body_from_source(source: str) -> str:
    dedented = textwrap.dedent(source)
    parsed   = ast.parse(dedented)
    node     = parsed.body[0]
    return _body_from_def_node(node)

def _extract_body_from_module_text(text: str, fn_name: str) -> str:
    """Find fn_name either at module level or inside any class (sync/async)."""
    parsed = ast.parse(text)

    # 1) module-level function
    for node in parsed.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == fn_name:
            return _body_from_def_node(node)

    # 2) methods inside classes
    for node in parsed.body:
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == fn_name:
                    return _body_from_def_node(item)

    return " "

def _body_from_def_node(def_node) -> str:
    """Return the body of a (async) function/method def as source, minus docstring."""
    body_nodes = list(def_node.body)
    # drop docstring if present
    if body_nodes and isinstance(body_nodes[0], ast.Expr):
        val = getattr(body_nodes[0], "value", None)
        if isinstance(val, ast.Constant) and isinstance(val.value, str):
            body_nodes = body_nodes[1:]
    try:
        return "\n".join(ast.unparse(n) for n in body_nodes)
    except Exception:
        # Fallback: at least return dedented original function source (if available)
        try:
            import inspect
            return textwrap.dedent(inspect.getsource(def_node))
        except Exception:
            return " "


class CustomTextWrapper(textwrap.TextWrapper):
    def _split(self, text):
        """
        Override the default splitting method to handle special characters and whitespace more effectively.
        """
        # Match sequences of non-whitespace characters, or any single whitespace character
        return re.findall(r'\S{1,' + str(self.width) + r'}|\S+|\s', text)


def wrap_text(text: str, width: int) -> str:
    """
    Wrap text to the specified width, handling special characters properly.

    Args:
        text (str): The text to wrap.
        width (int): The maximum width of each line.

    Returns:
        str: The wrapped text.
    """
    if not text:
        return ""

    # Normalize whitespace but keep newlines
    text = re.sub(r'[ \t]+', ' ', text)
    paragraphs = text.split('\n')

    # Create a custom text wrapper instance
    wrapper = CustomTextWrapper(width=width, break_long_words=True, replace_whitespace=False, tabsize=4,
                                fix_sentence_endings=True)

    # Wrap each paragraph individually
    wrapped_paragraphs = [wrapper.fill(paragraph) for paragraph in paragraphs]

    # Join the wrapped paragraphs with newlines and return the result
    return '\n'.join(wrapped_paragraphs)


def extract_keywords(text: str) -> list:
    """
    Extracts keywords from a given text string.

    Args:
        text (str): The text string to extract keywords from.

    Returns:
        list: A list of extracted keywords
    """
    if not text or not isinstance(text, str):
        return []
    # Remove punctuation and split into words
    words = re.findall(r'\b\w+\b', text.lower())
    # Filter out common words using a broader list of stop words
    _words = []
    for word in words:
        if word.isdigit():
            continue
        if word in VALID_WORDS:
            _words.append(word)
        elif word not in ENGLISH_STOP_WORDS and word not in CUSTOM_STOP_WORDS:
            _words.append(word)
    return _words


def filter_poor_tags(tags, threshold=1):
    """Filters out poor tags based on a threshold count."""
    tag_counter = Counter(tags)
    filtered_tags = [tag for tag, count in tag_counter.items() if count > threshold]
    return filtered_tags


def add_tags_to_commands(commands) -> dict:
    for command_name, command_info in commands.items():
        tags = []

        # Add keywords from command name
        tags.extend(extract_keywords(command_name))

        # Add keywords from name
        if 'name' in command_info and command_info['name']:
            tags.extend(extract_keywords(command_info['name']))

        # Add keywords from class name
        if 'class_name' in command_info and command_info['class_name']:
            tags.extend(extract_keywords(command_info['class_name']))

        # Add keywords from description
        if 'description' in command_info and command_info['description']:
            tags.extend(extract_keywords(command_info['description']))

        # Add keywords from arguments names
        if 'args' in command_info:
            for arg in command_info['args']:
                tags.extend(extract_keywords(arg['name']))

        # Add keywords from return type
        if 'return_type' in command_info:
            for return_type in command_info['return_type'] if isinstance(
                    command_info['return_type'], list) else [command_info['return_type']]:
                tags.extend(extract_keywords(return_type))

        # Add existing tags
        if 'tags' in command_info:
            for tag in command_info['tags']:
                tags.extend(extract_keywords(tag))

        # Filter and sort tags
        # filtered_tags = filter_poor_tags(tags)
        command_info['tags'] = list(set(tags))

    return commands


def clean_description(description: str) -> str:
    """
    Cleans up the description string by removing extra whitespace and trimming unnecessary parts.

    Args:
        description (str): The original description string.

    Returns:
        str: The cleaned description.
    """
    description = ' '.join(description.split())  # Remove extra whitespace
    for term in ['Args', 'Returns']:
        if term in description:
            description = description.split(term)[0]
    return description.strip()


def get_class_from_method(func) -> (str, str):
    """
    Returns the class name & function name from a given callable.

    Args:
        func: The callable function or method.

    Returns:
        tuple(cls, func): The class name and the callable name as a set.
    """
    func_name = func.__name__ if (
                inspect.ismethod(func) or inspect.isfunction(func) or inspect.iscoroutinefunction(func)) else None
    if not func_name:
        return None

    class_name = f""
    _path_parts = func.__qualname__.split('.')

    for i in range(len(_path_parts)):
        if _path_parts[i] == func_name:
            if _path_parts[i - 1] != '<locals>':
                class_name = _path_parts[i - 1]
                func_name = _path_parts[i]
            else:
                class_name = None

    return class_name, func_name

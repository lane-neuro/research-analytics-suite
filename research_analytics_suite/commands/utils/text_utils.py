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
import inspect
import ast
import re
import textwrap
from collections import Counter
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

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
    Get the body of a function as a string.
    """
    source = inspect.getsource(func)

    # Dedent the source code to remove leading spaces
    dedented_source = textwrap.dedent(source)

    # Parse the dedented source code
    parsed = ast.parse(dedented_source)

    function_node = parsed.body[0]  # Get the function node

    # Extract the body of the function
    function_body = function_node.body

    # Remove the docstring if it's present
    if isinstance(function_body[0], ast.Expr) and isinstance(function_body[0].value, ast.Str):
        function_body = function_body[1:]

    # Convert the AST nodes of the function body back to source code
    body_lines = [ast.unparse(node) for node in function_body]

    # Join the lines of the function body
    body_code = "\n".join(body_lines)
    return body_code


def wrap_text(text, width):
    """
    Wrap text to the specified width.
    """
    if not text:
        return ""
    lines = []
    words = text.split(' ')
    line = words.pop(0)
    for word in words:
        if len(line) + len(word) + 1 <= width:
            line += ' ' + word
        else:
            lines.append(line)
            line = word
    lines.append(line)
    lines = [line for line in lines if line]
    lines = f"\n".join(lines)
    return f"{lines}\n"


def extract_keywords(text):
    """Extracts keywords from a given text string."""
    if not text or not isinstance(text, str):
        return []
    # Remove punctuation and split into words
    words = re.findall(r'\b\w+\b', text.lower())
    # Filter out common words using a broader list of stop words
    _words = []
    for word in words:
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

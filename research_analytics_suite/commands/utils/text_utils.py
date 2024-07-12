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
import re


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
    return '\n'.join(lines)


def extract_keywords(text):
    """Extracts keywords from a given text string."""
    if not text:
        return []
    # Remove punctuation and split into words
    words = re.findall(r'\b\w+\b', text.lower())
    # Filter out common words (this can be expanded)
    common_words = {"the", "and", "to", "of", "in", "by", "for", "a", "an", "is", "if", "does", "as"}
    keywords = [word for word in words if word not in common_words]
    return keywords


def add_tags_to_commands(commands) -> dict:
    for command_name, command_info in commands.items():
        tags = set()

        # Add keywords from command name
        tags.update(extract_keywords(command_name))

        # Add keywords from class name
        if 'class_name' in command_info and command_info['class_name']:
            tags.update(extract_keywords(command_info['class_name']))

        # Add keywords from description
        if 'description' in command_info and command_info['description']:
            tags.update(extract_keywords(command_info['description']))

        # Add keywords from arguments names
        if 'args' in command_info:
            for arg in command_info['args']:
                tags.update(extract_keywords(arg['name']))

        # Convert tags to a sorted list and add to command info
        command_info['tags'] = sorted(tags)

    return commands

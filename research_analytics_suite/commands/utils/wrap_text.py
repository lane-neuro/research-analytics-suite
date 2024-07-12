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

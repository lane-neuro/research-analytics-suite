"""
Module description.

Longer description.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
from aioconsole import ainput


class Console_UI:
    """
    
    """

    def __init__(self):
        """
        
        """

        self.cmd_history = []

    async def exec(self):
        """
        Handles user-input data from the console.

        This method is responsible for asynchronously waiting for user input from the console.
        The input is then added to the command history of the DataEngine instance.

        Returns:
            str: User-input data from the console.
        """

        # Await user input from the console
        line = await ainput('->> ')

        # Add the input line to the command history
        self.cmd_history.append(line)

        return line

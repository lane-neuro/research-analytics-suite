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

import asyncio
from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler


class Operation:
    def __init__(self, run_forever: bool = False):
        self.status = "idle"
        self.progress = 0
        self.persistent = run_forever
        self.complete = False
        self.error_handler = ErrorHandler()
        self.sub_tasks = [
            asyncio.ensure_future(self.update_progress()),
            asyncio.ensure_future(self.error_handler.check_for_errors()),
        ]

    def progress(self):
        """
        Outputs the progress of an Operation.
        """
        return self.progress, self.status

    async def update_progress(self):
        """
        Updates the progress of an Operation.

        This method updates the progress of a given task until it's done.
        The progress is assumed to be stored in the 'progress' attribute of the Operation object.
        The method sleeps for 1 second between each check.

        Note:
            This is a coroutine and should be awaited.
        """

        while not self.complete:
            if self.status == "running":
                self.progress = self.progress + 1
                if self.progress >= 100:
                    self.complete = True
            await asyncio.sleep(1)

    async def check_for_errors(self):
        while not self.complete:
            if self.error_handler.has_error:
                self.status = "stopped"
                self.stop()
                break
            await asyncio.sleep(1)

    def start(self):
        try:
            self.status = "running"
            # execute operation
        except Exception as e:
            self.error_handler.handle_error(e, self)
            self.status = "error"

    def stop(self):
        try:
            self.status = "stopped"

        except Exception as e:
            self.error_handler.handle_error(e, self)
            self.status = "error"

    def pause(self):
        try:
            self.status = "paused"

        except Exception as e:
            self.error_handler.handle_error(e, self)
            self.status = "error"

    def resume(self):
        try:
            self.status = "running"

        except Exception as e:
            self.error_handler.handle_error(e, self)
            self.status = "error"

    def reset(self):
        try:
            self.status = "idle"

        except Exception as e:
            self.error_handler.handle_error(e, self)
            self.status = "error"

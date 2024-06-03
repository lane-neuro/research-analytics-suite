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


class TaskCounter:
    def __init__(self, logger):
        self.counter = 0
        self.logger = logger

    def new_task(self, name: str) -> str:
        self.counter += 1
        self.logger.info(f"TaskCounter.new_task: [NEW] [{self.counter}]{name}")
        return f"[{self.counter}]" + name

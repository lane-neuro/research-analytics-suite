"""
UpdateProgress Module

Contains functionality to update the progress of an operation.

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


async def update_progress(operation):
    """
    Update the progress of the operation. A basic timer for now.
    """
    while not operation.is_complete:
        if operation.status == "running":
            operation.progress += 1
        await asyncio.sleep(0.01)  # 100 updates per second

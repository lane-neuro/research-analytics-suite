"""
StopOperation Module

Contains functionality to stop an operation.

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


async def stop_operation(operation, child_operations=False):
    if operation.status == "running":
        try:
            operation.is_ready = False

            if child_operations and operation.child_operations is not None:
                await _stop_child_operations(operation)
            operation.task.cancel()
            operation.status = "stopped"
        except Exception as e:
            operation.handle_error(e)
        finally:
            await operation.add_log_entry(f"[STOP] {operation.name}")
    else:
        await operation.add_log_entry(f"[STOP] {operation.name} - Already stopped")


async def _stop_child_operations(operation):
    tasks = [op.stop() for op in operation.child_operations.values()]
    await asyncio.gather(*tasks)

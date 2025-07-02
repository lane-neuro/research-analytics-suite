"""
StorageInfo

This module contains the StorageInfo class, which gathers information about the system's storage devices.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import psutil


class StorageInfo:
    def __init__(self, logger):
        self.logger = logger

    def get_storage_info(self):
        """Get storage information.

        Returns:
            list: Information about the system's storage devices.
        """
        partitions = psutil.disk_partitions()
        storage_info = []
        for partition in partitions:
            usage = psutil.disk_usage(partition.mountpoint)
            storage_info.append({
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "fstype": partition.fstype,
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent": usage.percent
            })
        return storage_info

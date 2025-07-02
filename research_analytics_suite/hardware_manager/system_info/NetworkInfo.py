"""
NetworkInfo

This module contains the NetworkInfo class, which gathers information about the system's network interfaces.

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


class NetworkInfo:
    def __init__(self, logger):
        self.logger = logger

    def get_network_info(self):
        """Get network information.

        Returns:
            dict: Information about the system's network interfaces.
        """
        net_if_addrs = psutil.net_if_addrs()
        net_if_stats = psutil.net_if_stats()
        network_info = {
            "interfaces": net_if_addrs,
            "stats": net_if_stats
        }
        return network_info

"""
Mapped2DSpace Module


Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""


class Mapped2DSpace:
    """
    Mapped2DSpace class is used to create a 2D space to link operations via sequencers and dependencies.

    Attributes:
        _instance (Mapped2DSpace): The instance of the Mapped2DSpace class.
        _lock (asyncio.Lock): The lock to ensure thread safety.
        _space (dict): The dictionary to store the 2D space.
    """


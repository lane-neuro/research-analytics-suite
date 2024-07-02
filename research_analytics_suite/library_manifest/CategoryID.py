"""
CategoryID Module

The CategoryID enum module is used to store the unique identifiers of categories. It also has a method to get the
id and name of the category.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
from enum import Enum, unique


@unique
class CategoryID(Enum):
    def __init__(self, u_id, name):
        """
        Initializes the CategoryID with the given parameters.

        Args:
            u_id: The unique identifier of the category.
            name: The name of the category.
        """
        self._id = u_id
        self._name = name

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self):
        return self._name

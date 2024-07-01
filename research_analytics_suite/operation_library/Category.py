"""
Category Module

The Category class module is used to store the operations of a category. It also has a method to check if the category
is verified.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
from .utils import check_verified


class Category:
    def __init__(self, category_id, name):
        self.id = category_id
        self.name = name
        self.operations = []
        self.verified = check_verified(category_id)

    def add_operation(self, operation):
        self.operations.append(operation)

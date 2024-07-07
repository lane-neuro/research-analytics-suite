import pytest
import asyncio

import pytest_asyncio

from research_analytics_suite.library_manifest import Category


class TestCategory:
    @pytest_asyncio.fixture(autouse=True)
    async def setup_class(self):
        # This fixture runs before each test
        self.category_id = 1
        self.category_name = "Test Category"
        self.category = Category(self.category_id, self.category_name)
        await self.category.initialize()

    @pytest.mark.asyncio
    async def test_initialize(self):
        category = Category(self.category_id, self.category_name)
        await category.initialize()
        assert category._initialized is True

    @pytest.mark.asyncio
    async def test_category_id(self):
        assert self.category.category_id == self.category_id

    @pytest.mark.asyncio
    async def test_category_name(self):
        assert self.category.name == self.category_name

    @pytest.mark.asyncio
    async def test_register_operation(self):
        operation = "Test Operation"
        self.category.register_operation(operation)
        assert operation in self.category.operations

    @pytest.mark.asyncio
    async def test_add_subcategory(self):
        subcategory_id = 2
        subcategory_name = "Subcategory"
        subcategory = Category(subcategory_id, subcategory_name)
        await subcategory.initialize()

        self.category.add_subcategory(subcategory)
        assert subcategory_id in self.category.subcategories
        assert self.category.subcategories[subcategory_id] == subcategory

    @pytest.mark.asyncio
    async def test_get_operations(self):
        operation = "Test Operation"
        self.category.register_operation(operation)
        operations = self.category.get_operations()
        assert operation in operations

    @pytest.mark.asyncio
    async def test_get_operations_empty(self):
        empty_category = Category(2, "Empty Category")
        await empty_category.initialize()
        operations = empty_category.get_operations()
        assert operations == []

    @pytest.mark.asyncio
    async def test_repr(self):
        operation = "Test Operation"
        self.category.register_operation(operation)
        repr_str = repr(self.category)
        assert f"[ID:{self.category_id}]\t{self.category_name}" in repr_str
        assert operation in repr_str

    @pytest.mark.asyncio
    async def test_get_operations_none(self):
        # Directly setting the _operations attribute to None to simulate the scenario
        self.category._operations = None
        operations = self.category.get_operations()
        assert operations == []

import pytest
import pytest_asyncio

from research_analytics_suite.library_manifest import CategoryID


@pytest.mark.asyncio
class TestCategoryID:
    @pytest_asyncio.fixture(autouse=True)
    async def setup_class(self):
        self.categories = list(CategoryID)

    async def test_category_ids(self):
        expected_ids = [
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13
        ]
        for category, expected_id in zip(self.categories, expected_ids):
            assert category.id == expected_id

    async def test_category_names(self):
        expected_names = [
            "Numerical Data",
            "Categorical Data",
            "Text Data",
            "Time Series Data",
            "Big Data",
            "Cloud Computing",
            "Database",
            "Hypothesis Testing",
            "Data Collection",
            "Analysis Techniques",
            "Basic",
            "Intermediate",
            "Advanced"
        ]
        for category, expected_name in zip(self.categories, expected_names):
            assert category.name == expected_name

    async def test_subcategories(self):
        numerical_subcategories = {
            "Basic": (101, "Basic", {}),
            "Intermediate": (102, "Intermediate", {}),
            "Advanced": (103, "Advanced", {})
        }
        assert CategoryID.NUMERICAL.subcategories == numerical_subcategories

        categorical_subcategories = {
            "Basic": (201, "Basic", {}),
            "Intermediate": (202, "Intermediate", {}),
            "Advanced": (203, "Advanced", {})
        }
        assert CategoryID.CATEGORICAL.subcategories == categorical_subcategories

        text_subcategories = {
            "Basic": (301, "Basic", {}),
            "Intermediate": (302, "Intermediate", {}),
            "Advanced": (303, "Advanced", {})
        }
        assert CategoryID.TEXT.subcategories == text_subcategories

        time_series_subcategories = {
            "Basic": (401, "Basic", {}),
            "Intermediate": (402, "Intermediate", {}),
            "Advanced": (403, "Advanced", {})
        }
        assert CategoryID.TIME_SERIES.subcategories == time_series_subcategories

        big_data_subcategories = {
            "Hadoop": (501, "Hadoop", {}),
            "Spark": (502, "Spark", {})
        }
        assert CategoryID.BIG_DATA.subcategories == big_data_subcategories

        cloud_computing_subcategories = {
            "AWS": (601, "AWS", {}),
            "Azure": (602, "Azure", {}),
            "Google": (603, "Google Cloud", {})
        }
        assert CategoryID.CLOUD_COMPUTING.subcategories == cloud_computing_subcategories

        database_subcategories = {
            "SQL": (701, "SQL Queries", {}),
            "NoSQL": (702, "NoSQL", {})
        }
        assert CategoryID.DATABASE.subcategories == database_subcategories

        hypothesis_testing_subcategories = {
            "Statistical": (801, "Statistical Tests", {}),
            "Experimental": (802, "Experimental Design", {})
        }
        assert CategoryID.HYPOTHESIS_TESTING.subcategories == hypothesis_testing_subcategories

        data_collection_subcategories = {
            "Surveys": (901, "Surveys", {}),
            "Observational": (902, "Observational Studies", {})
        }
        assert CategoryID.DATA_COLLECTION.subcategories == data_collection_subcategories

        analysis_techniques_subcategories = {
            "Quantitative": (1001, "Quantitative Analysis", {}),
            "Qualitative": (1002, "Qualitative Analysis", {})
        }
        assert CategoryID.ANALYSIS_TECHNIQUES.subcategories == analysis_techniques_subcategories

        basic_operations_subcategories = {
            "Data Loading": (1101, "Data Loading", {}),
            "Simple Calculations": (1102, "Simple Calculations", {})
        }
        assert CategoryID.BASIC_OPERATIONS.subcategories == basic_operations_subcategories

        intermediate_operations_subcategories = {
            "Data Aggregation": (1201, "Data Aggregation", {}),
            "Intermediate Analysis": (1202, "Intermediate Analysis", {})
        }
        assert CategoryID.INTERMEDIATE_OPERATIONS.subcategories == intermediate_operations_subcategories

        advanced_operations_subcategories = {
            "Machine Learning Models": (1301, "Machine Learning Models", {}),
            "Deep Learning": (1302, "Deep Learning", {})
        }
        assert CategoryID.ADVANCED_OPERATIONS.subcategories == advanced_operations_subcategories

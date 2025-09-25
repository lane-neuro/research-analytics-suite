import pytest

from research_analytics_suite.library_manifest.CategoryID import CategoryID


class TestCategoryID:
    @pytest.fixture(autouse=True)
    def setup_class(self):
        self.categories = list(CategoryID)

    def test_category_ids(self):
        expected_ids = [
            1, 2, 3, 4, 5, 6, 7
        ]
        for category, expected_id in zip(self.categories, expected_ids):
            assert category.id == expected_id

    def test_category_names(self):
        expected_names = [
            "Descriptive Statistics",
            "Inferential Statistics",
            "Hypothesis Testing",
            "Regression & Correlation",
            "Time Series Analysis",
            "Data Preprocessing",
            "Data Visualization"
        ]
        for category, expected_name in zip(self.categories, expected_names):
            assert category.name == expected_name

    def test_subcategories(self):
        expected_subcategories = {
            "Descriptive Statistics": {
                "Central_Tendency": (101, "Central Tendency", {}),
                "Variability": (102, "Variability", {}),
                "Distribution": (103, "Distribution", {})
            },
            "Inferential Statistics": {
                "Parametric": (201, "Parametric Tests", {}),
                "Nonparametric": (202, "Non-parametric Tests", {}),
                "Confidence_Intervals": (203, "Confidence Intervals", {})
            },
            "Hypothesis Testing": {
                "T_Tests": (301, "T-Tests", {}),
                "Chi_Square": (302, "Chi-Square Tests", {}),
                "ANOVA": (303, "ANOVA", {})
            },
            "Regression & Correlation": {
                "Linear_Regression": (401, "Linear Regression", {}),
                "Multiple_Regression": (402, "Multiple Regression", {}),
                "Correlation": (403, "Correlation Analysis", {})
            },
            "Time Series Analysis": {
                "Trend_Analysis": (501, "Trend Analysis", {}),
                "Seasonal_Analysis": (502, "Seasonal Analysis", {}),
                "Forecasting": (503, "Forecasting", {})
            },
            "Data Preprocessing": {
                "Cleaning": (601, "Data Cleaning", {}),
                "Transformation": (602, "Data Transformation", {}),
                "Normalization": (603, "Data Normalization", {})
            },
            "Data Visualization": {
                "Basic_Plots": (701, "Basic Plots", {}),
                "Statistical_Plots": (702, "Statistical Plots", {}),
                "Advanced_Visualization": (703, "Advanced Visualization", {})
            }
        }
        for category in self.categories:
            assert category.subcategories == expected_subcategories[category.name]

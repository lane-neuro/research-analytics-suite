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
from enum import Enum


class CategoryID(Enum):
    DESCRIPTIVE_STATS = (1, "Descriptive Statistics", {
        "Central_Tendency": (101, "Central Tendency", {}),
        "Variability": (102, "Variability", {}),
        "Distribution": (103, "Distribution", {})
    })

    INFERENTIAL_STATS = (2, "Inferential Statistics", {
        "Parametric": (201, "Parametric Tests", {}),
        "Nonparametric": (202, "Non-parametric Tests", {}),
        "Confidence_Intervals": (203, "Confidence Intervals", {})
    })

    HYPOTHESIS_TESTING = (3, "Hypothesis Testing", {
        "T_Tests": (301, "T-Tests", {}),
        "Chi_Square": (302, "Chi-Square Tests", {}),
        "ANOVA": (303, "ANOVA", {})
    })

    REGRESSION = (4, "Regression & Correlation", {
        "Linear_Regression": (401, "Linear Regression", {}),
        "Multiple_Regression": (402, "Multiple Regression", {}),
        "Correlation": (403, "Correlation Analysis", {})
    })

    TIME_SERIES = (5, "Time Series Analysis", {
        "Trend_Analysis": (501, "Trend Analysis", {}),
        "Seasonal_Analysis": (502, "Seasonal Analysis", {}),
        "Forecasting": (503, "Forecasting", {})
    })

    DATA_PREPROCESSING = (6, "Data Preprocessing", {
        "Cleaning": (601, "Data Cleaning", {}),
        "Transformation": (602, "Data Transformation", {}),
        "Normalization": (603, "Data Normalization", {})
    })

    VISUALIZATION = (7, "Data Visualization", {
        "Basic_Plots": (701, "Basic Plots", {}),
        "Statistical_Plots": (702, "Statistical Plots", {}),
        "Advanced_Visualization": (703, "Advanced Visualization", {})
    })

    def __init__(self, u_id, name, subcategories):
        self._id = u_id
        self._name = name
        self._subcategories = subcategories

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def subcategories(self):
        return self._subcategories

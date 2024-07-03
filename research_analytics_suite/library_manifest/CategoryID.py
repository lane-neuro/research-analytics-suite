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
    NUMERICAL = (1, "Numerical Data", {
        "Basic": (101, "Basic Operations", {}),
        "Intermediate": (102, "Intermediate Operations", {}),
        "Advanced": (103, "Advanced Operations", {})
    })

    CATEGORICAL = (2, "Categorical Data", {
        "Basic": (201, "Basic Operations", {}),
        "Intermediate": (202, "Intermediate Operations", {}),
        "Advanced": (203, "Advanced Operations", {})
    })

    TEXT = (3, "Text Data", {
        "Basic": (301, "Basic Operations", {}),
        "Intermediate": (302, "Intermediate Operations", {}),
        "Advanced": (303, "Advanced Operations", {})
    })

    TIME_SERIES = (4, "Time Series Data", {
        "Basic": (401, "Basic Operations", {}),
        "Intermediate": (402, "Intermediate Operations", {}),
        "Advanced": (403, "Advanced Operations", {})
    })

    BIG_DATA = (5, "Big Data", {
        "Hadoop": (501, "Hadoop Operations", {}),
        "Spark": (502, "Spark Operations", {})
    })

    CLOUD_COMPUTING = (6, "Cloud Computing", {
        "AWS": (601, "AWS Operations", {}),
        "Azure": (602, "Azure Operations", {}),
        "Google": (603, "Google Cloud Operations", {})
    })

    DATABASE = (7, "Database", {
        "SQL": (701, "SQL Queries", {}),
        "NoSQL": (702, "NoSQL Operations", {})
    })

    HYPOTHESIS_TESTING = (8, "Hypothesis Testing", {
        "Statistical": (801, "Statistical Tests", {}),
        "Experimental": (802, "Experimental Design", {})
    })

    DATA_COLLECTION = (9, "Data Collection", {
        "Surveys": (901, "Surveys", {}),
        "Observational": (902, "Observational Studies", {})
    })

    ANALYSIS_TECHNIQUES = (10, "Analysis Techniques", {
        "Quantitative": (1001, "Quantitative Analysis", {}),
        "Qualitative": (1002, "Qualitative Analysis", {})
    })

    BASIC_OPERATIONS = (11, "Basic Operations", {
        "Data Loading": (1101, "Data Loading", {}),
        "Simple Calculations": (1102, "Simple Calculations", {})
    })

    INTERMEDIATE_OPERATIONS = (12, "Intermediate Operations", {
        "Data Aggregation": (1201, "Data Aggregation", {}),
        "Intermediate Analysis": (1202, "Intermediate Analysis", {})
    })

    ADVANCED_OPERATIONS = (13, "Advanced Operations", {
        "Machine Learning Models": (1301, "Machine Learning Models", {}),
        "Deep Learning": (1302, "Deep Learning", {})
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

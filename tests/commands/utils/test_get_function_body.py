import pytest

from research_analytics_suite.commands.utils.text_utils import extract_keywords


class TestExtractKeywords:

    def test_extract_keywords_valid_input(self):
        text = "Python is a high-level programming language."
        expected_keywords = ["python", "high", "level", "programming", "language"]
        assert extract_keywords(text) == expected_keywords

    def test_extract_keywords_with_stop_words(self):
        text = "Python is a programming language and it is very popular."
        expected_keywords = ["python", "programming", "language", "popular"]
        assert extract_keywords(text) == expected_keywords

    def test_extract_keywords_empty_input(self):
        text = ""
        expected_keywords = []
        assert extract_keywords(text) == expected_keywords

    def test_extract_keywords_non_string_input(self):
        text = None
        expected_keywords = []
        assert extract_keywords(text) == expected_keywords

    def test_extract_keywords_with_punctuation(self):
        text = "Python, the programming language, is great!"
        expected_keywords = ["python", "programming", "language", "great"]
        assert extract_keywords(text) == expected_keywords

    def test_extract_keywords_with_numbers(self):
        text = "Python 3.9 is the latest version."
        expected_keywords = ["python", "latest", "version"]
        assert extract_keywords(text) == expected_keywords

    def test_extract_keywords_with_custom_stop_words(self):
        text = "The quick brown fox jumps over the lazy dog."
        expected_keywords = ["quick", "brown", "fox", "jumps", "lazy", "dog"]
        assert extract_keywords(text) == expected_keywords

    def test_extract_keywords_with_valid_words(self):
        text = "This module provides various functions and methods for analysis."
        expected_keywords = ["module", "provides", "various", "functions", "methods", "analysis"]
        assert extract_keywords(text) == expected_keywords

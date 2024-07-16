import pytest
import re
from research_analytics_suite.commands.utils import wrap_text

class TestWrapText:

    def test_wrap_text_normal_case(self):
        text = "This is a sample text that needs to be wrapped."
        width = 10
        expected_output = "This is a\nsample\ntext that\nneeds to\nbe\nwrapped."
        assert wrap_text(text, width) == expected_output

    def test_wrap_text_empty_string(self):
        text = ""
        width = 10
        expected_output = ""
        assert wrap_text(text, width) == expected_output

    def test_wrap_text_single_long_word(self):
        text = "Supercalifragilisticexpialidocious"
        width = 10
        expected_output = "Supercalif\nragilistic\nexpialidoc\nious"
        assert wrap_text(text, width) == expected_output

    def test_wrap_text_width_larger_than_text(self):
        text = "Short text"
        width = 20
        expected_output = "Short text"
        assert wrap_text(text, width) == expected_output

    def test_wrap_text_exact_width(self):
        text = "1234567890"
        width = 10
        expected_output = "1234567890"
        assert wrap_text(text, width) == expected_output

    def test_wrap_text_multiple_spaces(self):
        text = "This  text  has  multiple  spaces."
        width = 10
        expected_output = "This text\nhas\nmultiple\nspaces."
        assert wrap_text(text, width) == expected_output

    def test_wrap_text_with_newline_characters(self):
        text = "This text\ncontains\nnewlines."
        width = 10
        expected_output = "This text\ncontains\nnewlines."
        assert wrap_text(text, width) == expected_output

    def test_wrap_text_leading_trailing_spaces(self):
        text = "   This text has leading and trailing spaces.   "
        width = 10
        expected_output = "This text\nhas\nleading\nand\ntrailing\nspaces."
        assert wrap_text(text.strip(), width) == expected_output

    def test_wrap_text_multiple_paragraphs(self):
        text = "This is the first paragraph.\n\nThis is the second paragraph."
        width = 15
        expected_output = "This is the\nfirst\nparagraph.\n\nThis is the\nsecond\nparagraph."
        assert wrap_text(text, width) == expected_output

    def test_wrap_text_empty_lines(self):
        text = "This is a line.\n\n\nThis is another line."
        width = 10
        expected_output = "This is a\nline.\n\n\nThis is\nanother\nline."
        assert wrap_text(text, width) == expected_output

    def test_wrap_text_special_characters(self):
        text = "Special characters: !@#$%^&*()_+{}|:\"<>?"
        width = 10
        expected_output = "Special\ncharacters\n:\n!@#$%^&*()\n_+{}|:\"<>?"
        assert wrap_text(text, width) == expected_output

    def test_wrap_text_mixed_whitespace_characters(self):
        text = "This\ttext contains\tdifferent\twhitespace."
        width = 10
        expected_output = "This text\ncontains\ndifferent\nwhitespace\n."
        assert wrap_text(re.sub(r'\s+', ' ', text), width) == expected_output

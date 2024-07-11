import pytest

from research_analytics_suite.commands.UserInputProcessor import parse_command


class TestParseCommand:

    def test_empty_string(self):
        assert parse_command("") == (None, [])

    def test_single_word(self):
        assert parse_command("command") == ("command", [])

    def test_multiple_words(self):
        assert parse_command("command arg1 arg2") == ("command", ["arg1", "arg2"])

    def test_leading_trailing_spaces(self):
        assert parse_command("  command arg1 arg2  ") == ("command", ["arg1", "arg2"])

    def test_mixed_spaces(self):
        assert parse_command("command   arg1  arg2") == ("command", ["arg1", "arg2"])

    def test_special_characters(self):
        assert parse_command("command !@# $%^") == ("command", ["!@#", "$%^"])

    def test_numeric_values(self):
        assert parse_command("command 123 456") == ("command", ["123", "456"])

    def test_empty_arguments(self):
        assert parse_command("command  ") == ("command", [])

    def test_mixed_alphanumeric(self):
        assert parse_command("command arg1 123") == ("command", ["arg1", "123"])

    def test_unicode_characters(self):
        assert parse_command("command 你好 世界") == ("command", ["你好", "世界"])

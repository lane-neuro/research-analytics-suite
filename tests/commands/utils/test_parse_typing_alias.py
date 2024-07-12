import pytest
from typing import Optional, List, Dict, Union, Tuple
from unittest.mock import patch

from research_analytics_suite.commands.utils.DynamicImport import parse_typing_alias


class TestParseTypingAlias:

    @patch('research_analytics_suite.commands.utils.DynamicImport.dynamic_import', side_effect=lambda x: {
        'int': int,
        'str': str,
        'float': float,
        'Optional[int]': Optional[int],
        'List[int]': List[int],
        'Dict[str, int]': Dict[str, int],
        'Union[int, str]': Union[int, str],
        'Tuple[int, str]': Tuple[int, str],
    }[x])
    def test_optional(self, mock_dynamic_import):
        assert parse_typing_alias('Optional', 'int') == Optional[int]
        assert parse_typing_alias('Optional', 'str') == Optional[str]

    @patch('research_analytics_suite.commands.utils.DynamicImport.dynamic_import', side_effect=lambda x: {
        'int': int,
        'str': str,
        'float': float,
        'Optional[int]': Optional[int],
        'List[int]': List[int],
        'Dict[str, int]': Dict[str, int],
        'Union[int, str]': Union[int, str],
        'Tuple[int, str]': Tuple[int, str],
    }[x])
    def test_list(self, mock_dynamic_import):
        assert parse_typing_alias('List', 'int') == List[int]
        assert parse_typing_alias('List', 'str') == List[str]

    @patch('research_analytics_suite.commands.utils.DynamicImport.dynamic_import', side_effect=lambda x: {
        'int': int,
        'str': str,
        'float': float,
        'Optional[int]': Optional[int],
        'List[int]': List[int],
        'Dict[str, int]': Dict[str, int],
        'Union[int, str]': Union[int, str],
        'Tuple[int, str]': Tuple[int, str],
    }.get(x, None))
    def test_dict(self, mock_dynamic_import):
        assert parse_typing_alias('Dict', 'str, int') == Dict[str, int]
        assert parse_typing_alias('Dict', 'int, float') == Dict[int, float]
        with pytest.raises(ValueError):
            parse_typing_alias('Dict', 'int')
        with pytest.raises(ValueError):
            parse_typing_alias('Dict', 'int, , str')

    @patch('research_analytics_suite.commands.utils.DynamicImport.dynamic_import', side_effect=lambda x: {
        'int': int,
        'str': str,
        'float': float,
        'Optional[int]': Optional[int],
        'List[int]': List[int],
        'Dict[str, int]': Dict[str, int],
        'Union[int, str]': Union[int, str],
        'Tuple[int, str]': Tuple[int, str],
    }[x])
    def test_union(self, mock_dynamic_import):
        assert parse_typing_alias('Union', 'int, str') == Union[int, str]
        assert parse_typing_alias('Union', 'int, str, float') == Union[int, str, float]

    @patch('research_analytics_suite.commands.utils.DynamicImport.dynamic_import', side_effect=lambda x: {
        'int': int,
        'str': str,
        'float': float,
        'Optional[int]': Optional[int],
        'List[int]': List[int],
        'Dict[str, int]': Dict[str, int],
        'Union[int, str]': Union[int, str],
        'Tuple[int, str]': Tuple[int, str],
    }[x])
    def test_tuple(self, mock_dynamic_import):
        assert parse_typing_alias('Tuple', 'int, str') == Tuple[int, str]
        assert parse_typing_alias('Tuple', 'int, str, float') == Tuple[int, str, float]

    @patch('research_analytics_suite.commands.utils.DynamicImport.dynamic_import', side_effect=lambda x: {
        'int': int,
        'str': str,
        'float': float,
        'Optional[int]': Optional[int],
        'List[int]': List[int],
        'Dict[str, int]': Dict[str, int],
        'Union[int, str]': Union[int, str],
        'Tuple[int, str]': Tuple[int, str],
    }[x])
    def test_invalid_alias(self, mock_dynamic_import):
        with pytest.raises(ValueError):
            parse_typing_alias('InvalidAlias', 'int')

    @patch('research_analytics_suite.commands.utils.DynamicImport.dynamic_import', side_effect=lambda x: {
        'int': int,
        'str': str,
        'float': float,
        'Optional[int]': Optional[int],
        'List[int]': List[int],
        'Dict[str, int]': Dict[str, int],
        'Union[int, str]': Union[int, str],
        'Tuple[int, str]': Tuple[int, str],
    }[x])
    def test_invalid_elements(self, mock_dynamic_import):
        with pytest.raises(ValueError):
            parse_typing_alias('Dict', 'int, str, float')

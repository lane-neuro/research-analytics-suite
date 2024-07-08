import pytest
import json
import pandas as pd
import fastavro

from research_analytics_suite.data_engine.data_streams.DataTypeDetector import detect_by_content


class TestDetectByContent:
    @pytest.mark.parametrize("file_content, expected_type", [
        ({"key": "value"}, "json"),
        ("col1,col2\nval1,val2\n", "csv"),
        (pd.DataFrame({"col1": ["val1"], "col2": ["val2"]}), "excel"),
        (pd.DataFrame({"col1": ["val1"], "col2": ["val2"]}), "parquet"),
        ([{"col1": "val1", "col2": "val2"}], "avro"),
        (pd.DataFrame({"col1": ["val1"], "col2": ["val2"]}), "hdf5"),
        ("This is some random content.", "unknown"),
    ])
    def test_detect_by_content(self, tmp_path, file_content, expected_type):
        file_path = tmp_path / "test_file"

        if expected_type == "json":
            file_path.write_text(json.dumps(file_content))
        elif expected_type == "csv":
            file_path.write_text(file_content)
        elif expected_type == "excel":
            file_content.to_excel(file_path, index=False)
        elif expected_type == "parquet":
            file_content.to_parquet(file_path)
        elif expected_type == "avro":
            schema = {
                "type": "record",
                "name": "test",
                "fields": [{"name": "col1", "type": "string"}, {"name": "col2", "type": "string"}]
            }
            with open(file_path, 'wb') as out:
                fastavro.writer(out, schema, file_content)
        elif expected_type == "hdf5":
            file_content.to_hdf(file_path, key='data', mode='w')
        else:
            file_path.write_text(file_content)

        result = detect_by_content(str(file_path))
        assert result == expected_type

    def test_detect_by_content_non_existent_file(self):
        with pytest.raises(Exception) as exc_info:
            detect_by_content("non_existent_file.txt")
        assert "Error detecting data type" in str(exc_info.value)

    def test_detect_by_content_empty_file(self, tmp_path):
        file_path = tmp_path / "empty.txt"
        file_path.write_text("")
        result = detect_by_content(str(file_path))
        assert result == "unknown"

    def test_detect_by_content_corrupted_file(self, tmp_path):
        file_path = tmp_path / "corrupted.txt"
        file_path.write_bytes(b"\x00\x00\x00\x00")
        result = detect_by_content(str(file_path))
        assert result == "unknown"

    def test_detect_by_content_unreadable_file(self, tmp_path):
        file_path = tmp_path / "unreadable.txt"
        file_path.write_bytes(b"\xff\xff\xff\xff")
        result = detect_by_content(str(file_path))
        assert result == "unknown"

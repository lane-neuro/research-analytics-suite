import json

import pandas as pd

from research_analytics_suite.data_engine.data_streams.DataTypeDetector import detect_by_content


class TestDetectByContent:
    def test_detect_json(self, tmp_path):
        # Create a temporary JSON file
        file_path = tmp_path / "test.json"
        content = json.dumps({"key": "value"})
        file_path.write_text(content)

        # Test detecting JSON file
        result = detect_by_content(str(file_path))
        assert result == "json"

    def test_detect_csv(self, tmp_path):
        # Create a temporary CSV file
        file_path = tmp_path / "test.csv"
        content = "col1,col2\nval1,val2\n"
        file_path.write_text(content)

        # Test detecting CSV file
        result = detect_by_content(str(file_path))
        assert result == "csv"

    def test_detect_excel(self, tmp_path):
        # Create a temporary Excel file
        file_path = tmp_path / "test.xlsx"
        df = pd.DataFrame({"col1": ["val1"], "col2": ["val2"]})
        df.to_excel(file_path, index=False)

        # Test detecting Excel file
        result = detect_by_content(str(file_path))
        assert result == "excel"

    def test_detect_parquet(self, tmp_path):
        # Create a temporary Parquet file
        file_path = tmp_path / "test.parquet"
        df = pd.DataFrame({"col1": ["val1"], "col2": ["val2"]})
        df.to_parquet(file_path)

        # Test detecting Parquet file
        result = detect_by_content(str(file_path))
        assert result == "parquet"

    def test_detect_avro(self, tmp_path):
        # Create a temporary Avro file
        file_path = tmp_path / "test.avro"
        schema = {
            "type": "record",
            "name": "test",
            "fields": [{"name": "col1", "type": "string"}, {"name": "col2", "type": "string"}]
        }
        records = [{"col1": "val1", "col2": "val2"}]

        import fastavro
        with open(file_path, 'wb') as out:
            fastavro.writer(out, schema, records)

        # Test detecting Avro file
        result = detect_by_content(str(file_path))
        assert result == "avro"

    def test_detect_hdf5(self, tmp_path):
        # Create a temporary HDF5 file
        file_path = tmp_path / "test.h5"
        df = pd.DataFrame({"col1": ["val1"], "col2": ["val2"]})
        df.to_hdf(file_path, key='data', mode='w')

        # Test detecting HDF5 file
        result = detect_by_content(str(file_path))
        assert result == "hdf5"

    def test_unknown_file_type(self, tmp_path):
        # Create a temporary file with unknown content
        file_path = tmp_path / "test.unknown"
        file_path.write_text("This is some random content.")

        # Test detecting unknown file type
        result = detect_by_content(str(file_path))
        assert result == "unknown"

"""
DataTypeDetector Module

This module defines the DataTypeDetector class, which provides methods to detect the type of data within
a file or data input source within the research analytics suite. It supports multiple data formats
including CSV, JSON, Excel, Parquet, Avro, and HDF5.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import json

import dask.dataframe as dd


class DataTypeDetector:
    """
    A class for detecting the type of data within a file or data input source.

    Methods:
        detect_type(file_path) - Detects the type of data based on the file extension or content.
        detect_by_content(file_path) - Detects the type of data by inspecting the content of the file.
        read_partial_file(file_path, size) - Reads a partial content from the file.
    """
    @staticmethod
    def detect_type(file_path):
        """
        Detects the type of data based on the file extension or content.

        Args:
            file_path (str): The path to the data file.

        Returns:
            str: The detected data type ('csv', 'json', 'excel', 'parquet', 'avro', 'hdf5', 'unknown').
        """
        return DataTypeDetector.detect_by_content(file_path)

    @staticmethod
    def detect_by_content(file_path):
        """
        Detects the type of data by inspecting the content of the file.

        Args:
            file_path (str): The path to the data file.

        Returns:
            str: The detected data type ('csv', 'json', 'excel', 'parquet', 'avro', 'hdf5', 'unknown').
        """
        try:
            content = DataTypeDetector.read_partial_file(file_path, 2048)

            # Try detecting JSON
            try:
                json.loads(content)
                return 'json'
            except json.JSONDecodeError:
                pass

            # Try detecting CSV
            if ',' in content or ';' in content:
                try:
                    dd.read_csv(file_path, blocksize=25e6).head(5)
                    return 'csv'
                except Exception as e:
                    print(f"Error reading CSV file: {e}")

            # Try detecting Excel
            if content.startswith(b'\x50\x4B\x03\x04') or content.startswith(b'\xD0\xCF\x11\xE0'):
                try:
                    dd.read_excel(file_path, nrows=5)
                    return 'excel'
                except Exception as e:
                    print(f"Error reading Excel file: {e}")

            # Try detecting Parquet
            try:
                dd.read_parquet(file_path).head(5)
                return 'parquet'
            except Exception as e:
                print(f"Error reading Parquet file: {e}")

            # Try detecting Avro
            try:
                import fastavro
                with open(file_path, 'rb') as f:
                    reader = fastavro.reader(f)
                    _ = next(reader)
                    return 'avro'
            except Exception as e:
                print(f"Error reading Avro file: {e}")

            # Try detecting HDF5
            try:
                dd.read_hdf(file_path, '/data').head(5)
                return 'hdf5'
            except Exception as e:
                print(f"Error reading HDF5 file: {e}")

        except Exception as e:
            print(f"Error reading file: {e}")

        return 'unknown'

    @staticmethod
    def read_partial_file(file_path, size):
        """
        Reads a partial content from the file.

        Args:
            file_path (str): The path to the file.
            size (int): The number of bytes to read.

        Returns:
            str: The partial content read from the file.
        """
        with open(file_path, 'rb') as file:
            return file.read(size).decode('utf-8', errors='ignore')

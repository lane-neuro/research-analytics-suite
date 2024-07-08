"""
DataTypeDetector Module

This module contains functions for detecting the type of data by inspecting the content of the file.

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
import fastavro
import pandas as pd


def read_partial_file(file_path: str, size: int, binary: bool = False) -> str or bytes:
    """
    Reads a partial content from the file.

    Args:
        file_path (str): The path to the file.
        size (int): The number of bytes to read.
        binary (bool): Whether to read the file as binary.

    Returns:
        str or bytes: The partial content read from the file.
    """
    mode = 'rb' if binary else 'r'
    with open(file_path, mode, encoding=None if binary else 'utf-8') as file:
        content = file.read(size)
        return content


def detect_by_content(file_path: str) -> str:
    """
    Detects the type of data by inspecting the content of the file.

    Args:
        file_path (str): The path to the data file.

    Returns:
        str: The detected data type ('csv', 'json', 'excel', 'parquet', 'avro', 'hdf5', 'unknown').
    """
    try:
        # First, try reading as text
        try:
            content = read_partial_file(file_path, 2048)
            binary_content = None
        except UnicodeDecodeError:
            content = None
            binary_content = read_partial_file(file_path, 2048, binary=True)

        if content:
            # Try detecting JSON
            try:
                json.loads(content)
                return 'json'
            except json.JSONDecodeError:
                pass

            # Try detecting CSV
            if ',' in content or ';' in content:
                try:
                    df = dd.read_csv(file_path, blocksize=25e6).compute()
                    df.head(5)
                    return 'csv'
                except Exception as e:
                    print(f"Error reading CSV file: {e}")

        if binary_content is None:
            binary_content = read_partial_file(file_path, 2048, binary=True)

        # Try detecting Excel
        if binary_content.startswith(b'\x50\x4B\x03\x04') or binary_content.startswith(b'\xD0\xCF\x11\xE0'):
            try:
                pd.read_excel(file_path, nrows=5)
                return 'excel'
            except Exception as e:
                print(f"Error reading Excel file: {e}")

        # Try detecting Parquet
        if binary_content.startswith(b'PAR1'):
            try:
                df = dd.read_parquet(file_path).compute()
                df.head(5)
                return 'parquet'
            except Exception as e:
                print(f"Error reading Parquet file: {e}")

        # Try detecting Avro
        if binary_content.startswith(b'Obj\x01'):
            try:
                with open(file_path, 'rb') as f:
                    reader = fastavro.reader(f)
                    _ = next(reader)
                    return 'avro'
            except Exception as e:
                print(f"Error reading Avro file: {e}")

        # Try detecting HDF5
        if binary_content.startswith(b'\x89HDF\r\n\x1A\n'):
            try:
                pd.read_hdf(file_path, '/data')
                return 'hdf5'
            except Exception as e:
                print(f"Error reading HDF5 file: {e}")

    except Exception as e:
        print(f"Error reading file: {e}")

    return 'unknown'
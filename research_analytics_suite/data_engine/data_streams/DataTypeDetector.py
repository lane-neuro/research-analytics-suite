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
from typing import Union


def read_partial_file(file_path: str, size: int, binary: bool = False) -> Union[str, bytes, None]:
    """
    Reads a partial content from the file.

    Args:
        file_path (str): The path to the file.
        size (int): The number of bytes to read.
        binary (bool): Whether to read the file as binary.

    Returns:
        str or bytes or None: The partial content read from the file.
    """
    mode = 'rb' if binary else 'r'
    try:
        with open(file_path, mode, encoding=None if binary else 'utf-8') as file:
            return file.read(size)
    except UnicodeDecodeError:
        if not binary:
            return read_partial_file(file_path, size, binary=True)
        raise
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except PermissionError:
        raise PermissionError(f"Permission denied: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading file: {e}")


def detect_by_content(file_path: str) -> str:
    """
    Detects the type of data by inspecting the content of the file.

    Args:
        file_path (str): The path to the data file.

    Returns:
        str: The detected data type ('csv', 'json', 'excel', 'parquet', 'avro', 'hdf5', 'unknown').
    """
    try:
        # Try reading as binary first
        binary_content = read_partial_file(file_path, 2048, binary=True)

        if binary_content:
            if is_excel(binary_content, file_path):
                return 'excel'
            if is_parquet(binary_content, file_path):
                return 'parquet'
            if is_avro(binary_content, file_path):
                return 'avro'
            if is_hdf5(binary_content, file_path):
                return 'hdf5'

        # If binary detection fails, try reading as text
        try:
            content = read_partial_file(file_path, 2048, binary=False)
            if content:
                if is_json(content):
                    return 'json'
                if is_csv(content, file_path):
                    return 'csv'
        except UnicodeDecodeError:
            pass

    except Exception as e:
        raise Exception(f"Error detecting data type: {e}")

    return 'unknown'


def is_json(content: str) -> bool:
    try:
        json.loads(content)
        return True
    except json.JSONDecodeError:
        return False


def is_csv(content: str, file_path: str) -> bool:
    if ',' in content or ';' in content:
        try:
            df = dd.read_csv(file_path, blocksize=25e6).compute()
            df.head(5)
            return True
        except Exception as e:
            raise Exception(f"Error reading CSV file: {e}")
    return False


def is_excel(binary_content: bytes, file_path: str) -> bool:
    if binary_content.startswith(b'\x50\x4B\x03\x04') or binary_content.startswith(b'\xD0\xCF\x11\xE0'):
        try:
            pd.read_excel(file_path, nrows=5)
            return True
        except Exception as e:
            raise Exception(f"Error reading Excel file: {e}")
    return False


def is_parquet(binary_content: bytes, file_path: str) -> bool:
    if binary_content.startswith(b'PAR1'):
        try:
            df = dd.read_parquet(file_path).compute()
            df.head(5)
            return True
        except Exception as e:
            raise Exception(f"Error reading Parquet file: {e}")
    return False


def is_avro(binary_content: bytes, file_path: str) -> bool:
    if binary_content.startswith(b'Obj\x01'):
        try:
            with open(file_path, 'rb') as f:
                reader = fastavro.reader(f)
                _ = next(reader)
                return True
        except Exception as e:
            raise Exception(f"Error reading Avro file: {e}")
    return False


def is_hdf5(binary_content: bytes, file_path: str) -> bool:
    if binary_content.startswith(b'\x89HDF\r\n\x1A\n'):
        try:
            pd.read_hdf(file_path, '/data')
            return True
        except Exception as e:
            raise Exception(f"Error reading HDF5 file: {e}")
    return False

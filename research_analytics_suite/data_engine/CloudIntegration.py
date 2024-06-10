"""
CloudIntegration Module

This module defines methods for integrating with cloud services like AWS S3 for scalable storage
and processing within the research analytics suite.

Author: Lane
"""

import boto3


class S3Integration:
    """
    A class for integrating with AWS S3.

    Attributes:
        s3_client (boto3.client): The S3 client instance.
    """
    def __init__(self, aws_access_key, aws_secret_key, region_name):
        """
        Initializes the S3Integration instance.

        Args:
            aws_access_key (str): The AWS access key.
            aws_secret_key (str): The AWS secret key.
            region_name (str): The AWS region name.
        """
        self._s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region_name
        )

    def upload_file(self, file_name, bucket, object_name=None):
        """
        Uploads a file to an S3 bucket.

        Args:
            file_name (str): The file to upload.
            bucket (str): The S3 bucket name.
            object_name (str): The S3 object name. If not specified, file_name is used.

        Returns:
            bool: True if file was uploaded, else False.
        """
        if object_name is None:
            object_name = file_name
        try:
            self._s3_client.upload_file(file_name, bucket, object_name)
            return True
        except Exception as e:
            print(f"Error uploading file: {e}")
            return False

    def download_file(self, bucket, object_name, file_name):
        """
        Downloads a file from an S3 bucket.

        Args:
            bucket (str): The S3 bucket name.
            object_name (str): The S3 object name.
            file_name (str): The file to download to.

        Returns:
            bool: True if file was downloaded, else False.
        """
        try:
            self._s3_client.download_file(bucket, object_name, file_name)
            return True
        except Exception as e:
            print(f"Error downloading file: {e}")
            return False

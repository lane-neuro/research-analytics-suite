"""
CloudIntegration Module

This module defines methods for integrating with cloud services like AWS S3 for scalable storage
and processing within the research analytics suite.

Author: Lane
"""

import boto3

from research_analytics_suite.commands import command, link_class_commands


@link_class_commands
class CloudIntegration:
    """
    A class for integrating with AWS S3.
    """
    def __init__(self, aws_access_key, aws_secret_key, region_name):
        """
        Initializes the CloudIntegration instance.

        Args:
            aws_access_key (str): The AWS access key.
            aws_secret_key (str): The AWS secret key.
            region_name (str): The AWS region name.
        """
        from research_analytics_suite.utils import CustomLogger
        self._logger = CustomLogger()

        self._s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region_name
        )

    @command
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
            self._logger.error(e, self.__class__.__name__)
            return False

    @command
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
            self._logger.error(e, self.__class__.__name__)
            return False

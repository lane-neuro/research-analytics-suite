import pytest
from unittest import mock

from research_analytics_suite.data_engine import CloudIntegration


@pytest.fixture
def mock_boto3_client():
    with mock.patch('boto3.client') as mock_client:
        yield mock_client


@pytest.fixture
def mock_custom_logger():
    with mock.patch('research_analytics_suite.utils.CustomLogger') as mock_logger:
        yield mock_logger


class TestCloudIntegration:
    @pytest.fixture(autouse=True)
    def setup_method(self, mock_boto3_client, mock_custom_logger):
        self.mock_s3_client = mock_boto3_client.return_value
        self.mock_logger_instance = mock_custom_logger.return_value
        self.cloud_integration = CloudIntegration(
            aws_access_key="test_access_key",
            aws_secret_key="test_secret_key",
            region_name="us-west-1"
        )
        self.cloud_integration._s3_client = self.mock_s3_client
        self.cloud_integration._logger = self.mock_logger_instance

    def test_upload_file_success(self):
        self.mock_s3_client.upload_file.return_value = None
        result = self.cloud_integration.upload_file("test_file.txt", "test_bucket")
        assert result is True
        self.mock_s3_client.upload_file.assert_called_once_with("test_file.txt", "test_bucket", "test_file.txt")

    def test_upload_file_failure(self):
        self.mock_s3_client.upload_file.side_effect = Exception("Upload failed")
        result = self.cloud_integration.upload_file("test_file.txt", "test_bucket")
        assert result is False
        self.mock_s3_client.upload_file.assert_called_once_with("test_file.txt", "test_bucket", "test_file.txt")
        self.mock_logger_instance.error.assert_called_once()

    def test_download_file_success(self):
        self.mock_s3_client.download_file.return_value = None
        result = self.cloud_integration.download_file("test_bucket", "test_object", "test_file.txt")
        assert result is True
        self.mock_s3_client.download_file.assert_called_once_with("test_bucket", "test_object", "test_file.txt")

    def test_download_file_failure(self):
        self.mock_s3_client.download_file.side_effect = Exception("Download failed")
        result = self.cloud_integration.download_file("test_bucket", "test_object", "test_file.txt")
        assert result is False
        self.mock_s3_client.download_file.assert_called_once_with("test_bucket", "test_object", "test_file.txt")
        self.mock_logger_instance.error.assert_called_once()

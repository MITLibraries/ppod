import os

import boto3
import pytest
from moto import mock_s3


@pytest.fixture(scope="session")
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"


@pytest.fixture()
def request_data_matching_file():
    request_data = {"filename-prefix": "upload/"}
    yield request_data


@pytest.fixture(scope="session")
def mocked_s3(aws_credentials):
    with mock_s3():
        with open("fixtures/pod.tar.gz", "rb") as pod_tar, open(
            "fixtures/empty.tar.gz", "rb"
        ) as empty_tar:
            s3 = boto3.client("s3", region_name="us-east-1")
            s3.create_bucket(Bucket="ppod")
            s3.put_object(
                Body=pod_tar,
                Bucket="ppod",
                Key="upload/pod.tar.gz",
            )
            s3.create_bucket(Bucket="empty_tar")
            s3.put_object(
                Body=empty_tar,
                Bucket="empty_tar",
                Key="upload/empty.tar.gz",
            )
            s3.create_bucket(Bucket="no_files")
            s3.create_bucket(Bucket="a_lot_of_files")
            for i in range(1001):
                s3.put_object(
                    Body=str(i),
                    Bucket="a_lot_of_files",
                    Key=f"upload/{i}.txt",
                )
            yield s3


@pytest.fixture(autouse=True)
def test_env():
    os.environ = {"WORKSPACE": "test", "BUCKET": "ppod"}
    yield

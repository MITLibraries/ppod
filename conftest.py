import os

import boto3
import pytest
import requests_mock
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


@pytest.fixture()
def mocked_pod():
    with requests_mock.Mocker() as m, open(
        "fixtures/pod_response.html", "r"
    ) as pod_response:
        request_headers = {"Authorization": "Bearer 1234abcd"}
        m.post(
            "http://example.example/organizations/ORG/uploads?stream=default",
            text=pod_response.read(),
            request_headers=request_headers,
        )
        yield m


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
    os.environ = {
        "ACCESS_TOKEN": "1234abcd",
        "BUCKET": "ppod",
        "POD_URL": "http://example.example/organizations/ORG/uploads?stream=",
        "STREAM": "default",
        "WORKSPACE": "test",
    }
    yield

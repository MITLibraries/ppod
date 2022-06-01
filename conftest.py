import os

import boto3
import pytest
import requests_mock
from moto import mock_s3, mock_ssm


@pytest.fixture(scope="session")
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"


@pytest.fixture()
def marcxml():
    with open("fixtures/marc.xml", "rb") as marcxml:
        yield marcxml


@pytest.fixture()
def marcxml_with_namespaces():
    with open("fixtures/marc_with_namespaces.xml", "rb") as marcxml_with_namespaces:
        yield marcxml_with_namespaces


@pytest.fixture(autouse=True, scope="session")
def mocked_pod():
    with requests_mock.Mocker() as m:
        request_headers = {"Authorization": "Bearer 1234abcd"}
        m.post(
            "http://example.example/organizations/ORG/uploads?stream=default",
            request_headers=request_headers,
        )
        m.post(
            "http://example.example/organizations/ORG/uploads?stream=not-a-stream",
            status_code=404,
        )
        yield m


@pytest.fixture(autouse=True, scope="session")
def mocked_s3(aws_credentials):
    with mock_s3():
        with open("fixtures/marc.tar.gz", "rb") as pod_tar, open(
            "fixtures/empty.tar.gz", "rb"
        ) as empty_tar:
            s3 = boto3.client("s3", region_name="us-east-1")
            s3.create_bucket(Bucket="ppod")
            s3.put_object(
                Body=pod_tar,
                Bucket="ppod",
                Key="upload/marc.tar.gz",
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


@pytest.fixture(autouse=True, scope="session")
def mocked_ssm():
    with mock_ssm():
        ssm = boto3.client("ssm", region_name="us-east-1")
        ssm.put_parameter(
            Name="/apps/ppod/stream-name",
            Value="default",
        )
        yield ssm


@pytest.fixture()
def request_data_matching_file():
    yield {"filename-prefix": "upload/"}


@pytest.fixture(autouse=True)
def test_env():
    os.environ = {
        "POD_ACCESS_TOKEN": "1234abcd",
        "BUCKET": "ppod",
        "POD_URL": "http://example.example/organizations/ORG/uploads?stream=",
        "WORKSPACE": "test",
    }
    yield

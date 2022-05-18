import json
import os

import boto3
import pytest
from moto import mock_iam, mock_s3


@pytest.fixture(scope="function")
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"


@pytest.fixture()
def aws_test_user(aws_credentials):
    with mock_iam():
        user_name = "test-user"
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["s3:ListBucket", "sqs:GetQueueUrl"],
                    "Resource": "*",
                },
                {
                    "Effect": "Deny",
                    "Action": [
                        "dynamodb:PutItem",
                        "dynamodb:Scan",
                        "s3:GetObject",
                        "ses:SendRawEmail",
                        "sqs:ReceiveMessage",
                        "sqs:SendMessage",
                        "ssm:GetParameter",
                    ],
                    "Resource": "*",
                },
            ],
        }
        client = boto3.client("iam", region_name="us-east-1")
        client.create_user(UserName=user_name)
        client.put_user_policy(
            UserName=user_name,
            PolicyName="policy1",
            PolicyDocument=json.dumps(policy_document),
        )
        yield client.create_access_key(UserName="test-user")["AccessKey"]


@pytest.fixture()
def get_request_matching_file():
    request_data = {
        "queryStringParameters": {
            "bucket": "ppod",
            "file_type": "tar.gz",
            "key_prefix": "upload",
        },
        "requestContext": {
            "http": {
                "method": "GET",
            },
        },
    }
    yield request_data


@pytest.fixture()
def get_request_no_files():
    request_data = {
        "queryStringParameters": {
            "bucket": "no_files",
            "file_type": "tar.gz",
            "key_prefix": "no_files",
        },
        "requestContext": {
            "http": {
                "method": "GET",
            },
        },
    }
    yield request_data


@pytest.fixture()
def get_request_no_matching_file():
    request_data = {
        "queryStringParameters": {
            "bucket": "ppod",
            "file_type": "tar.gz",
            "key_prefix": "download",
        },
        "requestContext": {
            "http": {
                "method": "GET",
            },
        },
    }
    yield request_data


@pytest.fixture(scope="function")
def mocked_s3(aws_credentials):
    with mock_s3():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="ppod")
        s3.put_object(
            Body=open("fixtures/pod.tar.gz", "rb"),
            Bucket="ppod",
            Key="upload/pod.tar.gz",
        )
        s3.create_bucket(Bucket="no_files")
        yield s3


@pytest.fixture(autouse=True)
def test_env():
    os.environ = {"WORKSPACE": "test"}
    yield

import logging
import os
import tarfile
from typing import IO, Generator, Optional

import sentry_sdk
import smart_open
from boto3 import client


def lambda_handler(event: dict, context: object) -> dict:
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    env = os.environ["WORKSPACE"]
    if sentry_dsn := os.getenv("SENTRY_DSN"):
        sentry_sdk.init(sentry_dsn, environment=env)
        logger.info(
            "Sentry DSN found, exceptions will be sent to Sentry with env=%s", env
        )
    file_count = 0
    bucket = os.environ["BUCKET"]
    s3_files = filter_files_in_bucket(
        bucket,
        event["filename-prefix"],
    )
    for s3_file in s3_files:
        logger.info(f"Processing file: {s3_file}")
        s3_file_content = smart_open.open(f"s3://{bucket}/{s3_file}", "rb")
        files = extract_files_from_tar(s3_file_content)
        for file in files:
            file  # do a thing
            file_count += 1
    return {"files-processed": file_count}


def extract_files_from_tar(
    tar_file: IO[bytes],
) -> Generator[Optional[IO[bytes]], None, None]:
    with tarfile.open(fileobj=tar_file) as tar:
        for member in tar.getmembers():
            file = tar.extractfile(member)
            yield file


def filter_files_in_bucket(bucket: str, prefix: str) -> Generator[str, None, None]:
    """Retrieve files in the specified bucket with the specified prefix."""
    s3_client = client("s3", region_name="us-east-1")
    paginator = s3_client.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=bucket, Prefix=prefix)
    try:
        for s3_object in (
            s3_object for page in pages for s3_object in page["Contents"]
        ):
            yield s3_object["Key"]
    except KeyError:
        raise KeyError(f"No files retrieved from {bucket} with prefix {prefix}")

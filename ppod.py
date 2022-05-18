import logging
import os
import tarfile
from typing import IO, Generator

import sentry_sdk
import smart_open
from boto3 import client


def lambda_handler(event: dict, context: object) -> str:
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    env = os.environ["WORKSPACE"]
    logger.info(
        "Running ppod with env=%s and log level=%s,",
        env,
        os.getenv("LOGGING_LEVEL", "DEBUG").upper(),
    )
    if sentry_dsn := os.getenv("SENTRY_DSN"):
        sentry_sdk.init(sentry_dsn, environment=env)
        logger.info(
            "Sentry DSN found, exceptions will be sent to Sentry with env=%s", env
        )
    file_count = 0
    try:
        bucket = event["queryStringParameters"]["bucket"]
        s3_files = filter_files_in_bucket(
            bucket,
            event["queryStringParameters"]["file_type"],
            event["queryStringParameters"]["key_prefix"],
        )
        for s3_file in s3_files:
            logger.info(f"Processing file: {s3_file}")
            s3_file_content = smart_open.open(f"s3://{bucket}/{s3_file}", "rb")
            files = extract_files_from_tar(s3_file_content)
            for file in files:
                file  # do a thing
                file_count += 1
    except KeyError:
        pass
    return f"Files processed: {file_count}"


def extract_files_from_tar(tar_file: IO[bytes]) -> Generator[IO[bytes], None, None]:
    tar = tarfile.open(fileobj=tar_file)
    for member in tar.getmembers():
        file = tar.extractfile(member)
        if file is not None:
            yield file


def filter_files_in_bucket(
    bucket: str, file_type: str, prefix: str = None
) -> Generator[str, None, None]:
    """Retrieve files with the specified file extension in the specified bucket with
    the specified prefix."""
    s3_client = client("s3", region_name="us-east-1")
    paginator = s3_client.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=bucket)
    for object in [
        object
        for page in pages
        for object in page["Contents"]
        if object["Key"].endswith(file_type) and prefix in object["Key"]
    ]:
        yield object["Key"]

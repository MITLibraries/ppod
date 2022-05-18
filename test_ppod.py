import logging

import pytest

from ppod import extract_files_from_tar, filter_files_in_bucket, lambda_handler


def test_ppod_configures_sentry_if_dsn_present(
    caplog, monkeypatch, mocked_s3, get_request_matching_file
):
    monkeypatch.setenv("SENTRY_DSN", "https://1234567890@00000.ingest.sentry.io/123456")
    caplog.set_level(logging.INFO)
    lambda_handler(get_request_matching_file, {})
    assert (
        "Sentry DSN found, exceptions will be sent to Sentry with env=test"
        in caplog.text
    )


def test_ppod_doesnt_configure_sentry_if_dsn_not_present(
    caplog, monkeypatch, mocked_s3, get_request_matching_file
):
    monkeypatch.delenv("SENTRY_DSN", raising=False)
    caplog.set_level(logging.INFO)
    lambda_handler(get_request_matching_file, {})
    assert "Sentry DSN found" not in caplog.text


def test_ppod_matching_files(caplog, monkeypatch, mocked_s3, get_request_matching_file):
    caplog.set_level(logging.INFO)
    output = lambda_handler(get_request_matching_file, {})
    assert output == "Files processed: 1"


def test_ppod_no_files(caplog, monkeypatch, mocked_s3, get_request_no_files):
    caplog.set_level(logging.INFO)
    output = lambda_handler(get_request_no_files, {})
    assert output == "Files processed: 0"


def test_ppod_no_matching_files(
    caplog, monkeypatch, mocked_s3, get_request_no_matching_file
):
    caplog.set_level(logging.INFO)
    output = lambda_handler(get_request_no_matching_file, {})
    assert output == "Files processed: 0"


def test_extract_files_from_tar():
    files = extract_files_from_tar(open("fixtures/pod.tar.gz", "rb"))
    for file in files:
        assert file.read() == open("fixtures/pod.xml", "rb").read()


def test_filter_files_in_bucket_with_matching_file(mocked_s3):
    files = filter_files_in_bucket("ppod", "tar.gz", "upload/")
    for file in files:
        assert file == "upload/pod.tar.gz"


def test_filter_files_in_bucket_with_no_file(mocked_s3):
    with pytest.raises(KeyError):
        files = filter_files_in_bucket("no_files", "tar.gz", "upload/")
        next(files)


def test_filter_files_in_bucket_without_matching_file(mocked_s3):
    with pytest.raises(StopIteration):
        files = filter_files_in_bucket("ppod", "tar.gz", "download/")
        next(files)

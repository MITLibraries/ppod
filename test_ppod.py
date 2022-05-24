import logging

import pytest

from ppod import (
    add_namespaces_to_alma_marcxml,
    extract_files_from_tar,
    filter_files_in_bucket,
    lambda_handler,
)


def test_ppod_configures_sentry_if_dsn_present(
    caplog, monkeypatch, mocked_s3, request_data_matching_file
):
    monkeypatch.setenv("SENTRY_DSN", "https://1234567890@00000.ingest.sentry.io/123456")
    caplog.set_level(logging.INFO)
    lambda_handler(request_data_matching_file, {})
    assert (
        "Sentry DSN found, exceptions will be sent to Sentry with env=test"
        in caplog.text
    )


def test_ppod_doesnt_configure_sentry_if_dsn_not_present(
    caplog, monkeypatch, mocked_s3, request_data_matching_file
):
    monkeypatch.delenv("SENTRY_DSN", raising=False)
    caplog.set_level(logging.INFO)
    lambda_handler(request_data_matching_file, {})
    assert "Sentry DSN found" not in caplog.text


def test_ppod_matching_files(mocked_s3, request_data_matching_file):
    output = lambda_handler(request_data_matching_file, {})
    assert output == {"files-processed": 1}


def test_ppod_no_files_raises_exception(
    monkeypatch, mocked_s3, request_data_matching_file
):
    monkeypatch.setenv("BUCKET", "no_files")
    with pytest.raises(KeyError):
        lambda_handler(request_data_matching_file, {})


def test_ppod_no_matching_files_raises_exception(mocked_s3):
    request_data = {"filename-prefix": "download/"}
    with pytest.raises(KeyError):
        lambda_handler(request_data, {})


def test_add_namespaces_to_alma_marcxml():
    modified_xml = add_namespaces_to_alma_marcxml(open("fixtures/pod.xml", "rb"))
    assert modified_xml == open("fixtures/pod_with_namespaces.xml", "r").read()


def test_extract_files_from_tar():
    files = extract_files_from_tar(open("fixtures/pod.tar.gz", "rb"))
    assert next(files).read() == open("fixtures/pod.xml", "rb").read()


def test_filter_files_in_bucket_with_1001_matching_file(mocked_s3):
    files = filter_files_in_bucket("a_lot_of_files", "upload/")
    assert len(list(files)) == 1001


def test_filter_files_in_bucket_with_matching_file(mocked_s3):
    files = filter_files_in_bucket("ppod", "upload/")
    assert next(files) == "upload/pod.tar.gz"


def test_filter_files_in_bucket_with_no_file(mocked_s3):
    with pytest.raises(KeyError):
        files = filter_files_in_bucket("no_files", "upload/")
        next(files)


def test_filter_files_in_bucket_without_matching_file(mocked_s3):
    with pytest.raises(KeyError):
        files = filter_files_in_bucket("ppod", "download/")
        next(files)

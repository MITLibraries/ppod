from importlib import reload

import pytest
import requests

import ppod
from ppod import (
    add_namespaces_to_alma_marcxml,
    extract_files_from_tar,
    filter_files_in_bucket,
    lambda_handler,
    post_file_to_pod,
)


def test_ppod_configures_sentry_if_dsn_present(caplog, monkeypatch):
    monkeypatch.setenv("SENTRY_DSN", "https://1234567890@00000.ingest.sentry.io/123456")
    reload(ppod)
    assert (
        "Sentry DSN found, exceptions will be sent to Sentry with env=test"
        in caplog.text
    )


def test_ppod_doesnt_configure_sentry_if_dsn_not_present(caplog, monkeypatch):
    monkeypatch.delenv("SENTRY_DSN", raising=False)
    reload(ppod)
    assert "No Sentry DSN found, exceptions will not be sent to Sentry" in caplog.text


def test_ppod_missing_workspace_env_raises_error(monkeypatch):
    monkeypatch.delenv("WORKSPACE", raising=False)
    with pytest.raises(RuntimeError) as e:
        lambda_handler({}, {})
    assert "Required env variable WORKSPACE is not set" in str(e)


def test_ppod_matching_files(request_data_matching_file):
    output = lambda_handler(request_data_matching_file, {})
    assert output == {"files_processed": 1}


def test_ppod_no_files_raises_exception(monkeypatch, request_data_matching_file):
    monkeypatch.setenv("BUCKET", "no_files")
    with pytest.raises(KeyError):
        lambda_handler(request_data_matching_file, {})


def test_ppod_empty_tar_raises_exception(monkeypatch, request_data_matching_file):
    monkeypatch.setenv("BUCKET", "empty_tar")
    with pytest.raises(ValueError):
        lambda_handler(request_data_matching_file, {})


def test_ppod_no_matching_files_raises_exception():
    request_data = {"filename-prefix": "download/"}
    with pytest.raises(KeyError):
        lambda_handler(request_data, {})


def test_add_namespaces_to_alma_marcxml(marcxml, marcxml_with_namespaces):
    modified_xml = add_namespaces_to_alma_marcxml(marcxml)
    assert modified_xml.read() == marcxml_with_namespaces.read()


def test_add_namespaces_to_alma_marcxml_invalid_xml_raises_exception():
    with pytest.raises(ValueError), open("fixtures/invalid.xml", "rb") as invalid_xml:
        add_namespaces_to_alma_marcxml(invalid_xml)


def test_extract_files_from_tar(marcxml):
    with open("fixtures/marc.tar.gz", "rb") as pod_tar:
        files = extract_files_from_tar(pod_tar)
        assert next(files).read() == marcxml.read()


def test_filter_files_in_bucket_with_1001_matching_file():
    files = filter_files_in_bucket("a_lot_of_files", "upload/")
    assert len(list(files)) == 1001


def test_filter_files_in_bucket_with_matching_file():
    files = filter_files_in_bucket("ppod", "upload/")
    assert next(files) == "upload/marc.tar.gz"


def test_filter_files_in_bucket_with_no_file():
    with pytest.raises(KeyError):
        files = filter_files_in_bucket("no_files", "upload/")
        next(files)


def test_filter_files_in_bucket_without_matching_file():
    with pytest.raises(KeyError):
        files = filter_files_in_bucket("ppod", "download/")
        next(files)


def test_post_files_to_pod_success(marcxml_with_namespaces):
    response = post_file_to_pod(
        "http://example.example/organizations/ORG/uploads?stream=default",
        {"Authorization": "Bearer 1234abcd"},
        "pod_file",
        marcxml_with_namespaces,
    )
    assert response.status_code == 200


def test_post_files_to_pod_bad_url_raises_error(marcxml_with_namespaces):
    with pytest.raises(requests.exceptions.HTTPError):
        post_file_to_pod(
            "http://example.example/organizations/ORG/uploads?stream=not-a-stream",
            {"Authorization": "Bearer 1234abcd"},
            "pod_file",
            marcxml_with_namespaces,
        )

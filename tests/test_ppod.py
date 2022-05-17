import logging

from lambdas.ppod import lambda_handler


def test_ppod_configures_sentry_if_dsn_present(caplog, monkeypatch):
    monkeypatch.setenv("WORKSPACE", "test")
    monkeypatch.setenv("SENTRY_DSN", "https://1234567890@00000.ingest.sentry.io/123456")
    caplog.set_level(logging.INFO)
    output = lambda_handler({}, {})
    assert (
        "Sentry DSN found, exceptions will be sent to Sentry with env=test"
        in caplog.text
    )
    assert output == "lambda"


def test_webhook_doesnt_configure_sentry_if_dsn_not_present(caplog, monkeypatch):
    monkeypatch.setenv("WORKSPACE", "test")
    monkeypatch.delenv("SENTRY_DSN", raising=False)
    caplog.set_level(logging.INFO)
    output = lambda_handler({}, {})
    assert "Sentry DSN found" not in caplog.text
    assert output == "lambda"

from lambdas.ping import lambda_handler


def test_ping():
    assert lambda_handler({}, {}) == "pong"


def test_ping_always_pongs():
    assert lambda_handler({"hallo": "cheese"}, {}) == "pong"

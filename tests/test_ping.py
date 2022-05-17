from lambdas.ping import lambda_handler


def test_ping():
    assert lambda_handler({}, {}) == "pong"

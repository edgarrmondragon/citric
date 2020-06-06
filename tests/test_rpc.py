"""Tests for JSON-RPC."""
import pytest

from citric.exceptions import (
    LimeSurveyApiError,
    LimeSurveyError,
    LimeSurveyStatusError,
)
from citric.rpc import BaseRPC, Session

URL = "http://example.com"
USERNAME = "limeuser"
PASSWORD = "limesecret"


@pytest.fixture(scope="function")
def session(requests_mock):
    requests_mock.post(URL, text='{"result":"123456","error":null,"id":1}')
    session = Session(URL, USERNAME, PASSWORD)

    yield session

    requests_mock.post(URL, text='{"result":"OK","error":null,"id":1}')
    session.close()


def test_json_rpc(session, requests_mock):
    requests_mock.post(session.url, text='{"error":null,"result":"OK","id":1}')

    response = session.rpc("some_method")

    assert response.result == "OK"
    assert response.error is None
    assert response.id == 1


@pytest.mark.parametrize("message", [None, "Test message"])
def test_status_exception(message):
    default = LimeSurveyError.default

    with pytest.raises(LimeSurveyError) as excinfo:
        raise LimeSurveyError(message)

    exc = excinfo.value
    assert str(exc) == message if message is not None else default


def test_bad_spec():
    with pytest.raises(NotImplementedError):

        class BadRPC(BaseRPC):
            pass

        bad_spec = BadRPC()
        bad_spec.invoke()


def test_session_context(requests_mock):
    requests_mock.post(URL, text='{"result":"123456","error":null,"id":1}')

    with Session(URL, USERNAME, PASSWORD) as session:
        assert session.key == "123456"


def test_disabled_interface(session, requests_mock):
    requests_mock.post(session.url, text="")

    with pytest.raises(LimeSurveyError):
        session.rpc("some_method")


def test_api_error(session, requests_mock):
    requests_mock.post(session.url, text='{"result":null,"error":"Some Error","id":1}')

    with pytest.raises(LimeSurveyApiError) as excinfo:
        session.rpc("not_valid")

    exc = excinfo.value
    assert exc.response.result is None
    assert exc.response.error == "Some Error"


def test_status_error(session, requests_mock):
    requests_mock.post(
        session.url, text='{"result":{"status":"Status Message"},"error":null,"id":1}'
    )

    with pytest.raises(LimeSurveyStatusError) as excinfo:
        session.rpc("not_valid")

    exc = excinfo.value
    assert exc.response.result == {"status": "Status Message"}
    assert exc.response.error is None

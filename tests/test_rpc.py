"""Tests for JSON-RPC."""
from typing import Optional

import pytest
from requests_mock import Mocker

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
def session(requests_mock: Mocker):
    """Create a LimeSurvey Session fixture."""
    requests_mock.post(URL, text='{"result":"123456","error":null,"id":1}')
    session = Session(URL, USERNAME, PASSWORD)

    yield session

    requests_mock.post(URL, text='{"result":"OK","error":null,"id":1}')
    session.close()


def test_json_rpc(session: Session, requests_mock: Mocker):
    """Test JSON RPC response structure."""
    requests_mock.post(session.url, text='{"error":null,"result":"OK","id":1}')

    response = session.rpc("some_method")

    assert response.result == "OK"
    assert response.error is None
    assert response.id == 1


@pytest.mark.parametrize("message", [None, "Test message"])
def test_status_exception(message: Optional[str]):
    """Test LimeSurvey exception strings."""
    default = LimeSurveyError.default

    with pytest.raises(LimeSurveyError) as excinfo:
        raise LimeSurveyError(message)

    assert str(excinfo.value) == (message if message is not None else default)


def test_bad_spec():
    """Test missing methods raises error."""
    with pytest.raises(NotImplementedError):

        class BadRPC(BaseRPC):
            pass

        bad_spec = BadRPC()
        bad_spec.invoke(URL, USERNAME, PASSWORD)


def test_session_context(requests_mock: Mocker):
    """Test context creates a session key."""
    requests_mock.post(URL, text='{"result":"123456","error":null,"id":1}')

    with Session(URL, USERNAME, PASSWORD) as session:
        assert session.key == "123456"


def test_disabled_interface(session: Session, requests_mock: Mocker):
    """Test empty response."""
    requests_mock.post(session.url, text="")

    with pytest.raises(LimeSurveyError) as excinfo:
        session.rpc("some_method")

    assert str(excinfo.value) == "RPC interface not enabled"


def test_api_error(session: Session, requests_mock: Mocker):
    """Test non-null error raises LimeSurveyApiError."""
    requests_mock.post(session.url, text='{"result":null,"error":"Some Error","id":1}')

    with pytest.raises(LimeSurveyApiError) as excinfo:
        session.rpc("not_valid")

    assert str(excinfo.value) == "Some Error"


def test_status_error(session: Session, requests_mock: Mocker):
    """Test result with status key raises LimeSurveyStatusError."""
    requests_mock.post(
        session.url, text='{"result":{"status":"Status Message"},"error":null,"id":1}'
    )

    with pytest.raises(LimeSurveyStatusError) as excinfo:
        session.rpc("not_valid")

    assert str(excinfo.value) == "Status Message"

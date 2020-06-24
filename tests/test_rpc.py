"""Tests for RPC low-level calls."""
from typing import Any, Optional

import json
import pytest
from requests import HTTPError
from requests_mock import Mocker
from xmlrpc.client import dumps, Fault

from citric.exceptions import (
    LimeSurveyApiError,
    LimeSurveyError,
    LimeSurveyStatusError,
)
from citric.method import Method
from citric.rpc import XMLRPC
from citric.rpc.base import BaseRPC
from citric.session import Session


def faker(
    result: Any, error: Optional[Any] = None, spec: str = "json", request_id: int = 1,
) -> str:
    """Build a fake raw RPC response."""
    if spec == "json":
        return json.dumps({"error": error, "result": result, "id": request_id})

    elif spec == "xml":
        if error is None:
            return dumps((result,), methodresponse=True)
        else:
            return dumps(Fault("123", error), methodresponse=True)

    return ""


@pytest.fixture(scope="session")
def url() -> str:
    """Dummy LimeSurvey RemoteControl URL."""
    return "http://example.com"


@pytest.fixture(scope="session")
def username() -> str:
    """Dummy LimeSurvey username."""
    return "limeuser"


@pytest.fixture(scope="session")
def password() -> str:
    """Dummy LimeSurvey password."""
    return "limesecret"


@pytest.fixture(scope="function")
def session(url: str, username: str, password: str, requests_mock: Mocker):
    """Create a LimeSurvey Session fixture."""
    requests_mock.post(url, text=faker("123456"))
    session = Session(url, username, password)

    yield session

    requests_mock.post(url, text=faker("OK"))
    session.close()


@pytest.fixture(scope="function")
def xml_session(url: str, username: str, password: str, requests_mock: Mocker):
    """Create a LimeSurvey Session fixture with XML-RPC."""
    requests_mock.post(url, text=faker("123456", spec="xml"))
    session = Session(url, username, password, spec=XMLRPC())

    yield session

    requests_mock.post(url, text=faker("OK", spec="xml"))
    session.close()


def test_method() -> None:
    """Test method magic."""
    m1 = Method(lambda x, *args: f"{x}({','.join(args)})", "hello")
    m2 = m1.world

    assert m2("a", "b", "c") == "hello.world(a,b,c)"


def test_json_rpc(session: Session, requests_mock: Mocker):
    """Test JSON RPC response structure."""
    requests_mock.post(session.url, text=faker("OK"))

    result = session.some_method()

    assert result == "OK"


def test_xml_rpc(xml_session: Session, requests_mock: Mocker):
    """Test XML RPC response structure."""
    requests_mock.post(xml_session.url, text=faker("OK", spec="xml"))

    result = xml_session.some_method()

    assert result == "OK"


def test_http_error(session: Session, requests_mock: Mocker):
    """Test HTTP errors."""
    requests_mock.post(session.url, text=faker("OK"), status_code=500)

    with pytest.raises(HTTPError):
        session.some_method()


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
        bad_spec.invoke()


def test_session_context(url: str, username: str, password: str, requests_mock: Mocker):
    """Test context creates a session key."""
    requests_mock.post(url, text=faker("123456"))

    with Session(url, username, password) as session:
        assert not session.closed
        assert session.key == "123456"

    assert session.closed
    assert session.key is None

    with pytest.raises(AttributeError) as excinfo:
        session.key = "123456"

    assert str(excinfo.value) == "can't set attribute"

    with pytest.raises(AttributeError) as excinfo:
        session.closed = False

    assert str(excinfo.value) == "can't set attribute"


def test_disabled_interface(session: Session, requests_mock: Mocker):
    """Test empty response."""
    requests_mock.post(session.url, text="")

    with pytest.raises(LimeSurveyError) as excinfo:
        session.some_method()

    assert str(excinfo.value) == "RPC interface not enabled"


def test_api_error(session: Session, requests_mock: Mocker):
    """Test non-null error raises LimeSurveyApiError."""
    requests_mock.post(session.url, text=faker(None, "Some Error"))

    with pytest.raises(LimeSurveyApiError) as excinfo:
        session.not_valid()

    assert str(excinfo.value) == "Some Error"


def test_status_error(session: Session, requests_mock: Mocker):
    """Test result with status key raises LimeSurveyStatusError."""
    requests_mock.post(session.url, text=faker({"status": "Status Message"}))

    with pytest.raises(LimeSurveyStatusError) as excinfo:
        session.not_valid()

    assert str(excinfo.value) == "Status Message"


def test_status_ok(session: Session, requests_mock: Mocker):
    """Test result with OK status does not raise errors."""
    requests_mock.post(session.url, text=faker({"status": "OK"}))

    result = session.not_valid()

    assert result["status"] == "OK"


def test_mismatching_request_id(session: Session, requests_mock: Mocker):
    """Test result with status key raises LimeSurveyStatusError."""
    requests_mock.post(session.url, text=faker("OK", request_id=2))

    with pytest.raises(LimeSurveyError) as excinfo:
        session.not_valid()

    assert (
        str(excinfo.value) == "ID 2 in response does not match the one in the request 1"
    )

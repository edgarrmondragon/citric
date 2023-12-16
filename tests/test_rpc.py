"""Integration tests for the RPC client."""

from __future__ import annotations

import json
import random
import sys

import pytest
import requests

from citric.exceptions import (
    InvalidJSONResponseError,
    LimeSurveyApiError,
    LimeSurveyStatusError,
    ResponseMismatchError,
    RPCInterfaceNotEnabledError,
)
from citric.method import Method
from citric.session import Session

from .conftest import LimeSurveyMockAdapter

if sys.version_info >= (3, 11):
    SET_PROPERTY_MESSAGE_REGEX = "property .* of 'Session' object has no setter"
else:
    SET_PROPERTY_MESSAGE_REGEX = "can't set attribute"


class RPCOffAdapter(LimeSurveyMockAdapter):
    """Mock adapter with RPC interface turned off."""

    rpc_interface = "off"


@pytest.fixture(scope="session")
def off_session(url: str) -> requests.Session:
    """Session with interface turned off."""
    requests_session = requests.Session()
    requests_session.mount(url, RPCOffAdapter())
    return requests_session


def test_method():
    """Test method magic."""
    m1 = Method(lambda x, *args: f"{x}({','.join(args)})", "hello")
    m2 = m1.world

    assert m1("x", "y") == "hello(x,y)"
    assert m2("a", "b", "c") == "hello.world(a,b,c)"


def test_json_rpc(session: Session):
    """Test JSON RPC response structure."""
    result = session.__ok()

    assert result == "OK"


def test_http_error(session: Session):
    """Test HTTP errors."""
    with pytest.raises(requests.HTTPError):
        session.__http_error()


def test_session(
    url: str,
    username: str,
    password: str,
    mock_session: requests.Session,
):
    """Test context creates a session key."""
    with Session(url, username, password, requests_session=mock_session) as session:
        assert not session.closed
        assert session.key == LimeSurveyMockAdapter.session_key


def test_session_auth_plugin(
    url: str,
    username: str,
    password: str,
    mock_session: requests.Session,
):
    """Test context creates a session key and uses auth plugin."""
    with Session(
        url,
        username,
        password,
        requests_session=mock_session,
        auth_plugin="AuthLDAP",
    ) as session:
        assert not session.closed
        assert session.key == LimeSurveyMockAdapter.ldap_session_key


def test_closed_session(
    url: str,
    username: str,
    password: str,
    mock_session: requests.Session,
):
    """Test context closes session."""
    with Session(url, username, password, requests_session=mock_session) as session:
        pass

    assert session.closed
    assert session.key is None

    with pytest.raises(AttributeError, match=SET_PROPERTY_MESSAGE_REGEX):
        session.key = "123456"  # type: ignore[misc]

    with pytest.raises(AttributeError, match=SET_PROPERTY_MESSAGE_REGEX):
        session.closed = False  # type: ignore[misc]


def test_empty_response(session: Session):
    """Test empty response."""
    with pytest.raises(RPCInterfaceNotEnabledError, match="RPC interface not enabled"):
        session.__disabled()


def test_non_json_response(session: Session):
    """Test non-JSON response."""
    with pytest.raises(InvalidJSONResponseError, match="Received a non-JSON response"):
        session.__not_json()


def test_json_encode_error(session: Session):
    """Test JSON encoding error."""

    class NotSerializable:
        """Not serializable."""

        def __init__(self, value: int):
            self.value = value

    with pytest.raises(
        TypeError,
        match="Object of type NotSerializable is not JSON serializable",
    ):
        session._invoke("json_encode_error", NotSerializable(123))


def test_custom_json_encoder(
    url: str,
    username: str,
    password: str,
    mock_session: requests.Session,
):
    """Test custom JSON encoder."""

    class NotSerializable:
        """Not serializable."""

        def __init__(self, value: int):
            self.value = value

    class CustomJSONEncoder(json.JSONEncoder):
        """Custom JSON encoder."""

        def default(self, o: object) -> object:
            return o.value if isinstance(o, NotSerializable) else super().default(o)

    session = Session(
        url,
        username,
        password,
        requests_session=mock_session,
        json_encoder=CustomJSONEncoder,
    )

    session._invoke("json_encode_error", NotSerializable(123))


def test_api_error(session: Session):
    """Test non-null error raises LimeSurveyApiError."""
    with pytest.raises(LimeSurveyApiError, match="API Error!"):
        session.__api_error()


def test_status_error(session: Session):
    """Test result with status key raises LimeSurveyStatusError."""
    with pytest.raises(LimeSurveyStatusError, match="Status Error!"):
        session.__status_error()


def test_status_ok(session: Session):
    """Test result with OK status does not raise errors."""
    result = session.__status_ok()

    assert result["status"] == "OK"


def test_mismatching_request_id(session: Session, monkeypatch: pytest.MonkeyPatch):
    """Test result with status key raises LimeSurveyStatusError."""

    def randint(a: int, b: int) -> int:
        return 123

    monkeypatch.setattr(random, "randint", randint)

    with pytest.raises(
        ResponseMismatchError,
        match="Response ID 2 does not match request ID 123",
    ):
        session.__bad_id()

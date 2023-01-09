"""Tests for RPC low-level calls."""

from __future__ import annotations

import random
import sys

import pytest
import requests

from citric.exceptions import (
    LimeSurveyApiError,
    LimeSurveyError,
    LimeSurveyStatusError,
    ResponseMismatchError,
)
from citric.method import Method
from citric.session import Session

from .conftest import LimeSurveyMockAdapter


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


def test_session_context(
    url: str,
    username: str,
    password: str,
    mock_session: requests.Session,
):
    """Test context creates a session key."""
    with Session(url, username, password, requests_session=mock_session) as session:
        assert not session.closed
        assert session.key == LimeSurveyMockAdapter.session_key

    with Session(
        url,
        username,
        password,
        requests_session=mock_session,
        auth_plugin="AuthLDAP",
    ) as session:
        assert not session.closed
        assert session.key == LimeSurveyMockAdapter.ldap_session_key

    assert session.closed
    assert session.key is None

    message_regex = (
        "can't set attribute"
        if sys.version_info < (3, 11)
        else "property .* of 'Session' object has no setter"
    )

    with pytest.raises(AttributeError, match=message_regex):
        session.key = "123456"

    with pytest.raises(AttributeError, match=message_regex):
        session.closed = False


def test_empty_response(session: Session):
    """Test empty response."""
    with pytest.raises(LimeSurveyError, match="RPC interface not enabled"):
        session.__disabled()


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

    def randint(a, b):
        return 123

    monkeypatch.setattr(random, "randint", randint)

    with pytest.raises(
        ResponseMismatchError, match="Response ID 2 does not match request ID 123"
    ):
        session.__bad_id()

"""Tests for RPC low-level calls."""
from typing import Callable

import pytest
from requests import HTTPError
from requests_mock import Mocker

from citric.exceptions import (
    LimeSurveyApiError,
    LimeSurveyError,
    LimeSurveyStatusError,
)
from citric.method import Method
from citric.session import Session

PostCallable = Callable[..., None]


def test_method():
    """Test method magic."""
    m1 = Method(lambda x, *args: f"{x}({','.join(args)})", "hello")
    m2 = m1.world

    assert m2("a", "b", "c") == "hello.world(a,b,c)"


def test_json_rpc(session: Session, post_mock: Callable[..., None]):
    """Test JSON RPC response structure."""
    post_mock("OK")

    result = session.some_method()

    assert result == "OK"


def test_http_error(session: Session, post_mock: Callable[..., None]):
    """Test HTTP errors."""
    post_mock("OK", status_code=500)

    with pytest.raises(HTTPError):
        session.some_method()


def test_session_context(
    url: str, username: str, password: str, post_mock: Callable[..., None],
):
    """Test context creates a session key."""
    post_mock("123456")

    with Session(url, username, password) as session:
        assert not session.closed
        assert session.key == "123456"

    assert session.closed
    assert session.key is None

    with pytest.raises(AttributeError, match="can't set attribute"):
        session.key = "123456"

    with pytest.raises(AttributeError, match="can't set attribute"):
        session.closed = False


def test_disabled_interface(session: Session, requests_mock: Mocker):
    """Test empty response."""
    requests_mock.post(session.url, text="")

    with pytest.raises(LimeSurveyError, match="RPC interface not enabled"):
        session.some_method()


def test_api_error(session: Session, post_mock: Callable[..., None]):
    """Test non-null error raises LimeSurveyApiError."""
    post_mock(None, "Some Error")

    with pytest.raises(LimeSurveyApiError, match="Some Error"):
        session.not_valid()


def test_status_error(session: Session, post_mock: Callable[..., None]):
    """Test result with status key raises LimeSurveyStatusError."""
    post_mock({"status": "Status Message"})

    with pytest.raises(LimeSurveyStatusError, match="Status Message"):
        session.not_valid()


def test_status_ok(session: Session, post_mock: Callable[..., None]):
    """Test result with OK status does not raise errors."""
    post_mock({"status": "OK"})

    result = session.not_valid()

    assert result["status"] == "OK"


def test_mismatching_request_id(session: Session, post_mock: Callable[..., None]):
    """Test result with status key raises LimeSurveyStatusError."""
    post_mock("OK", request_id=2)

    with pytest.raises(
        LimeSurveyError, match="response does not match the one in the request"
    ):
        session.not_valid()

"""Tests for RPC low-level calls."""
from typing import Callable

import pytest
import requests

from citric.exceptions import (
    LimeSurveyApiError,
    LimeSurveyError,
    LimeSurveyStatusError,
)
from citric.method import Method
from citric.session import Session

from .conftest import LimeSurveyMockAdapter


class RPCOffAdapter(LimeSurveyMockAdapter):
    """Mock adapter with RPC interface turned off."""

    rpc_interface = "off"


@pytest.fixture(scope="session")
def off_session_factory(url: str) -> Callable[[], requests.Session]:
    """Session with interface turned off."""

    def factory() -> requests.Session:
        """Session factory."""
        requests_session = requests.Session()
        requests_session.mount(url, RPCOffAdapter())
        return requests_session

    return factory


def test_method():
    """Test method magic."""
    m1 = Method(lambda x, *args: f"{x}({','.join(args)})", "hello")
    m2 = m1.world

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
    mock_session_factory: Callable[[], requests.Session],
):
    """Test context creates a session key."""
    with Session(url, username, password, mock_session_factory) as session:
        assert not session.closed
        assert session.key == LimeSurveyMockAdapter.session_key

    assert session.closed
    assert session.key is None

    with pytest.raises(AttributeError, match="can't set attribute"):
        session.key = "123456"

    with pytest.raises(AttributeError, match="can't set attribute"):
        session.closed = False


def test_interface_off(
    url: str,
    username: str,
    password: str,
    off_session_factory: Callable[[], requests.Session],
):
    """Test effect of JSON RPC not enabled."""
    with pytest.raises(LimeSurveyError, match="JSON RPC interface is not enabled"):
        Session(url, username, password, off_session_factory)


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


def test_mismatching_request_id(session: Session):
    """Test result with status key raises LimeSurveyStatusError."""
    with pytest.raises(
        LimeSurveyError, match=r"Response ID \d+ does not match request ID \d+"
    ):
        session.__bad_id()

"""Tests for RPC low-level calls."""
import pytest
import requests

from citric.exceptions import (
    LimeSurveyApiError,
    LimeSurveyError,
    LimeSurveyStatusError,
)
from citric.method import Method
from citric.session import _BaseSession, Session

from .conftest import LimeSurveyMockAdapter


def test_method():
    """Test method magic."""
    m1 = Method(lambda x, *args: f"{x}({','.join(args)})", "hello")
    m2 = m1.world

    assert m2("a", "b", "c") == "hello.world(a,b,c)"


def test_base_session():
    """Test session abstraction."""

    class TestSession(_BaseSession):
        pass

    session = TestSession("mock://lime", "user", "secret")

    with pytest.raises(NotImplementedError):
        session.rpc("test", 1, 2, 3)


def test_json_rpc(session: Session):
    """Test JSON RPC response structure."""
    result = session.__ok()

    assert result == "OK"


def test_http_error(session: Session):
    """Test HTTP errors."""
    with pytest.raises(requests.HTTPError):
        session.__http_error()


def test_session_context(
    url: str, username: str, password: str, adapter: LimeSurveyMockAdapter,
):
    """Test context creates a session key."""
    requests_session = requests.Session()
    requests_session.mount(url, adapter)

    with Session(url, username, password, requests_session) as session:
        assert not session.closed
        assert session.key == adapter.session_key

    assert session.closed
    assert session.key is None

    with pytest.raises(AttributeError, match="can't set attribute"):
        session.key = "123456"

    with pytest.raises(AttributeError, match="can't set attribute"):
        session.closed = False


def test_disabled_interface(session: Session):
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
        LimeSurveyError, match="response does not match the one in the request"
    ):
        session.__bad_id()

"""Tests for RPC low-level calls."""
from typing import Any, Callable, Optional

import json
import pytest
from requests import HTTPError
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

PostCallable = Callable[[Any], None]


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


def test_method():
    """Test method magic."""
    m1 = Method(lambda x, *args: f"{x}({','.join(args)})", "hello")
    m2 = m1.world

    assert m2("a", "b", "c") == "hello.world(a,b,c)"


@pytest.fixture(scope="function")
def xml_session(
    url: str, username: str, password: str, post_mock: Callable[[Any], None],
):
    """Create a LimeSurvey Session fixture with XML-RPC."""
    post_mock(
        [{"text": faker("123456", spec="xml")}, {"text": faker("OK", spec="xml")}]
    )
    session = Session(url, username, password, spec=XMLRPC())

    yield session

    session.close()


def test_json_rpc(session: Session, post_mock: Callable[[Any], None]):
    """Test JSON RPC response structure."""
    post_mock(text=faker("OK"))

    result = session.some_method()

    assert result == "OK"


def test_xml_rpc(xml_session: Session, post_mock: Callable[[Any], None]):
    """Test XML RPC response structure."""
    post_mock(text=faker("OK", spec="xml"))

    result = xml_session.some_method()

    assert result == "OK"


def test_http_error(session: Session, post_mock: Callable[[Any], None]):
    """Test HTTP errors."""
    post_mock(text=faker("OK"), status_code=500)

    with pytest.raises(HTTPError):
        session.some_method()


def test_bad_spec():
    """Test missing methods raises error."""
    with pytest.raises(NotImplementedError):

        class BadRPC(BaseRPC):
            pass

        bad_spec = BadRPC()
        bad_spec.invoke()


def test_session_context(
    url: str, username: str, password: str, post_mock: Callable[[Any], None],
):
    """Test context creates a session key."""
    post_mock(text=faker("123456"))

    with Session(url, username, password) as session:
        assert not session.closed
        assert session.key == "123456"

    assert session.closed
    assert session.key is None

    with pytest.raises(AttributeError, match="can't set attribute"):
        session.key = "123456"

    with pytest.raises(AttributeError, match="can't set attribute"):
        session.closed = False


def test_disabled_interface(session: Session, post_mock: Callable[[Any], None]):
    """Test empty response."""
    post_mock(text="")

    with pytest.raises(LimeSurveyError, match="RPC interface not enabled"):
        session.some_method()


def test_api_error(session: Session, post_mock: Callable[[Any], None]):
    """Test non-null error raises LimeSurveyApiError."""
    post_mock(text=faker(None, "Some Error"))

    with pytest.raises(LimeSurveyApiError, match="Some Error"):
        session.not_valid()


def test_status_error(session: Session, post_mock: Callable[[Any], None]):
    """Test result with status key raises LimeSurveyStatusError."""
    post_mock(text=faker({"status": "Status Message"}))

    with pytest.raises(LimeSurveyStatusError, match="Status Message"):
        session.not_valid()


def test_status_ok(session: Session, post_mock: Callable[[Any], None]):
    """Test result with OK status does not raise errors."""
    post_mock(text=faker({"status": "OK"}))

    result = session.not_valid()

    assert result["status"] == "OK"


def test_mismatching_request_id(session: Session, post_mock: Callable[[Any], None]):
    """Test result with status key raises LimeSurveyStatusError."""
    post_mock(text=faker("OK", request_id=2))

    with pytest.raises(
        LimeSurveyError, match="response does not match the one in the request"
    ):
        session.not_valid()

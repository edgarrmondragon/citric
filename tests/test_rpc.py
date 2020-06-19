"""Tests for JSON-RPC."""
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
from citric.rpc.base import BaseRPC
from citric.rpc.xml import XMLRPC
from citric.session import Session

URL = "http://example.com"
USERNAME = "limeuser"
PASSWORD = "limesecret"
JSON_HEADERS = {"Content-Type": "text/javascript;charset=UTF-8"}
XML_HEADERS = {"Content-Type": "text/html;charset=UTF-8"}
DUMMY_RESPONSE = {"error": None, "result": "OK"}
JSON_RESPONSE = json.dumps({**DUMMY_RESPONSE, "id": 1})
XML_RESPONSE = dumps((DUMMY_RESPONSE["result"],), methodresponse=True,)


def make_fake_response(
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


JSON_RESPONSE = make_fake_response("OK")
XML_RESPONSE = make_fake_response("OK", spec="xml")


@pytest.fixture(scope="function")
def session(requests_mock: Mocker):
    """Create a LimeSurvey Session fixture."""
    requests_mock.post(URL, text=make_fake_response("123456"), headers=JSON_HEADERS)
    session = Session(URL, USERNAME, PASSWORD)

    yield session

    requests_mock.post(URL, text=JSON_RESPONSE, headers=JSON_HEADERS)
    session.close()


@pytest.fixture(scope="function")
def xml_session(requests_mock: Mocker):
    """Create a LimeSurvey Session fixture with XML-RPC."""
    requests_mock.post(
        URL, text=make_fake_response("123456", spec="xml"), headers=XML_HEADERS,
    )
    session = Session(URL, USERNAME, PASSWORD, spec=XMLRPC())

    yield session

    requests_mock.post(URL, text=XML_RESPONSE, headers=XML_HEADERS)
    session.close()


def test_method() -> None:
    """Test method magic."""
    m1 = Method(lambda x, *args: f"{x}({','.join(args)})", "hello")
    m2 = m1.world

    assert m2("a", "b", "c") == "hello.world(a,b,c)"


def test_json_rpc(session: Session, requests_mock: Mocker):
    """Test JSON RPC response structure."""
    requests_mock.post(session.url, text=JSON_RESPONSE, headers=JSON_HEADERS)

    result = session.some_method()

    assert result == "OK"


def test_xml_rpc(xml_session: Session, requests_mock: Mocker):
    """Test XML RPC response structure."""
    requests_mock.post(xml_session.url, text=XML_RESPONSE, headers=XML_HEADERS)

    result = xml_session.some_method()

    assert result == "OK"


def test_http_error(session: Session, requests_mock: Mocker):
    """Test HTTP errors."""
    requests_mock.post(
        URL, text=make_fake_response(""), headers=JSON_HEADERS, status_code=500,
    )

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
        bad_spec.invoke(URL, USERNAME, PASSWORD)


def test_session_context(requests_mock: Mocker):
    """Test context creates a session key."""
    requests_mock.post(URL, text=make_fake_response("123456"), headers=JSON_HEADERS)

    with Session(URL, USERNAME, PASSWORD) as session:
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
    requests_mock.post(session.url, text="", headers=JSON_HEADERS)

    with pytest.raises(LimeSurveyError) as excinfo:
        session.some_method()

    assert str(excinfo.value) == "RPC interface not enabled"


def test_api_error(session: Session, requests_mock: Mocker):
    """Test non-null error raises LimeSurveyApiError."""
    requests_mock.post(
        session.url, text=make_fake_response(None, "Some Error"), headers=JSON_HEADERS,
    )

    with pytest.raises(LimeSurveyApiError) as excinfo:
        session.not_valid()

    assert str(excinfo.value) == "Some Error"


def test_status_error(session: Session, requests_mock: Mocker):
    """Test result with status key raises LimeSurveyStatusError."""
    requests_mock.post(
        session.url,
        text=make_fake_response({"status": "Status Message"}),
        headers=JSON_HEADERS,
    )

    with pytest.raises(LimeSurveyStatusError) as excinfo:
        session.not_valid()

    assert str(excinfo.value) == "Status Message"


def test_status_ok(session: Session, requests_mock: Mocker):
    """Test result with OK status does not raise errors."""
    requests_mock.post(
        session.url, text=make_fake_response({"status": "OK"}), headers=JSON_HEADERS,
    )

    result = session.not_valid()

    assert result["status"] == "OK"


def test_mismatching_request_id(session: Session, requests_mock: Mocker):
    """Test result with status key raises LimeSurveyStatusError."""
    requests_mock.post(
        session.url, text=make_fake_response("OK", request_id=2), headers=JSON_HEADERS,
    )

    with pytest.raises(LimeSurveyError) as excinfo:
        session.not_valid()

    assert (
        str(excinfo.value) == "ID 2 in response does not match the one in the request 1"
    )

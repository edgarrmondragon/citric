"""pytest fixtures."""
import json
from typing import Any, Mapping, Optional, Tuple, Union

import pytest
import requests
from requests.adapters import BaseAdapter

from citric.session import Session


class LimeSurveyMockAdapter(BaseAdapter):
    """Requests adapter that mocks LSRC2 API calls."""

    api_error_methods = {"__api_error"}
    status_error_methods = {"__status_error"}
    http_error_methods = {"__http_error"}
    ok_methods = {"__ok", "release_session_key"}
    status_ok_methods = {"__status_ok", "activate_tokens", "delete_survey"}

    session_key = "123456"
    status_ok = {"status": "OK"}
    rpc_interface = "json"

    ldap_session_key = "ldap-key"

    def send(
        self,
        request: requests.PreparedRequest,
        stream: bool = False,
        timeout: Union[None, float, Tuple[float, float], Tuple[float, None]] = None,
        verify: Union[bool, str] = True,
        cert: Optional[Any] = None,
        proxies: Optional[Mapping[str, str]] = None,
    ):
        """Sends a mocked request."""
        request_data = json.loads(request.body or "{}")

        response = requests.Response()
        response.__setattr__("_content", b"")
        response.status_code = 200

        method = request_data["method"]
        params = request_data["params"]
        request_id = request_data.get("id", 1)

        output = {"result": None, "error": None, "id": request_id}

        if method == "__disabled":
            return response

        if method in self.api_error_methods:
            output["error"] = "API Error!"
        elif method in self.status_error_methods:
            output["result"] = {"status": "Status Error!"}
        elif method in self.http_error_methods:
            response.status_code = 500
        elif method in self.ok_methods:
            output["result"] = "OK"
        elif method in self.status_ok_methods:
            output["result"] = self.status_ok
        elif method == "__bad_id":
            output["id"] = 2
        elif method == "get_session_key":
            output["result"] = (
                self.ldap_session_key if params[2] == "AuthLDAP" else self.session_key
            )
        elif method == "get_site_settings" and params[1] == "RPCInterface":
            output["result"] = self.rpc_interface

        response.__setattr__("_content", json.dumps(output).encode())

        return response

    def close(self):
        """Cleans up adapter specific items."""


@pytest.fixture(scope="session")
def url() -> str:
    """Dummy LimeSurvey RemoteControl URL."""
    return "lime://example.com"


@pytest.fixture(scope="session")
def mock_session(url: str) -> requests.Session:
    """Factory for building mock sessions."""
    requests_session = requests.Session()
    requests_session.mount(url, LimeSurveyMockAdapter())
    return requests_session


@pytest.fixture(scope="session")
def username() -> str:
    """Dummy LimeSurvey username."""
    return "limeuser"


@pytest.fixture(scope="session")
def password() -> str:
    """Dummy LimeSurvey password."""
    return "limesecret"


@pytest.fixture(scope="session")
def session(
    url: str,
    username: str,
    password: str,
    mock_session: requests.Session,
):
    """Create a LimeSurvey Session fixture."""
    session = Session(url, username, password, requests_session=mock_session)

    yield session

    session.close()

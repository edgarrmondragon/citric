"""pytest fixtures."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest
import requests
from requests.adapters import BaseAdapter

from citric.exceptions import LimeSurveyStatusError
from citric.session import Session

if TYPE_CHECKING:
    from typing import Any, Mapping


def pytest_addoption(parser: pytest.Parser):
    """Add command line options to pytest."""
    parser.addoption(
        "--database-type",
        action="store",
        default="postgres",
        choices=["postgres", "mysql"],
        help="Database used for integration tests.",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]):
    """Modify test collection."""
    if config.getoption("--database-type") == "postgres":
        return
    xfail = pytest.mark.xfail(reason="This test fails on MySQL")
    for item in items:
        if "xfail_mysql" in item.keywords:
            item.add_marker(xfail)


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

    def _handle_json_response(
        self,
        method: str,
        params: list[Any],
        request_id: int,
    ) -> requests.Response:
        response = requests.Response()
        response.status_code = 200
        output: dict[str, Any] = {"result": None, "error": None, "id": request_id}

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

    def send(  # noqa: PLR0913
        self,
        request: requests.PreparedRequest,
        stream: bool = False,  # noqa: FBT001, FBT002
        timeout: float | tuple[float, float] | tuple[float, None] | None = None,
        verify: bool | str = True,  # noqa: FBT002
        cert: Any | None = None,
        proxies: Mapping[str, str] | None = None,
    ):
        """Send a mocked request."""
        request_data = json.loads(request.body or "{}")
        method = request_data["method"]
        params = request_data["params"]
        request_id = request_data.get("id", 1)

        if method == "__disabled":
            response = requests.Response()
            response.status_code = 200
            return response

        if method == "__not_json":
            response = requests.Response()
            response.status_code = 200
            response.__setattr__("_content", b"this is not json")
            return response

        return self._handle_json_response(method, params, request_id)

    def close(self):
        """Clean up adapter specific items."""


@pytest.fixture(scope="session")
def url() -> str:
    """Get a dummy LimeSurvey RemoteControl URL."""
    return "lime://example.com"


@pytest.fixture(scope="session")
def mock_session(url: str) -> requests.Session:
    """Create a mock requests session."""
    requests_session = requests.Session()
    requests_session.mount(url, LimeSurveyMockAdapter())
    return requests_session


@pytest.fixture(scope="session")
def username() -> str:
    """Get a dummy LimeSurvey username."""
    return "limeuser"


@pytest.fixture(scope="session")
def password() -> str:
    """Get a dummy LimeSurvey password."""
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

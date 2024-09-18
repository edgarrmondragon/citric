"""pytest fixtures."""

from __future__ import annotations

import json
import os
import typing as t
from importlib.metadata import version

import pytest
import requests
from dotenv import load_dotenv
from requests.adapters import BaseAdapter

from citric.session import Session

load_dotenv()


def _add_integration_skip(
    item: pytest.Item,
    value: str | None,
    reason: str,
) -> None:
    """Add a skip marker to integration tests if the required option is not set."""
    if value is None:
        marker = pytest.mark.skip(reason=reason)
        item.add_marker(marker)


def _from_env_var(
    env_var: str,
    default: str | None = None,
) -> str | None:
    """Get a value from an environment variable or return a default."""
    return os.environ.get(env_var, default)


def pytest_addoption(parser: pytest.Parser):
    """Add command line options to pytest."""
    parser.addoption(
        "--database-type",
        action="store",
        choices=["postgres", "mysql"],
        help="Database used for integration tests.",
        default=_from_env_var("BACKEND"),
    )

    parser.addoption(
        "--limesurvey-url",
        action="store",
        help="URL of the LimeSurvey instance to test against.",
        default=_from_env_var("LS_URL"),
    )

    parser.addoption(
        "--limesurvey-username",
        action="store",
        help="Username of the LimeSurvey user to test against.",
        default=_from_env_var("LS_USER"),
    )

    parser.addoption(
        "--limesurvey-password",
        action="store",
        help="Password of the LimeSurvey user to test against.",
        default=_from_env_var("LS_PASSWORD"),
    )

    parser.addoption(
        "--mailhog-url",
        action="store",
        help="URL of the MailHog instance to test against.",
        default=_from_env_var("MAILHOG_URL", "http://localhost:8025"),
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]):
    """Modify test collection."""
    backend = config.getoption("--database-type")
    url = config.getoption("--limesurvey-url")
    username = config.getoption("--limesurvey-username")
    password = config.getoption("--limesurvey-password")

    xfail_mysql = pytest.mark.xfail(reason="This test fails on MySQL")
    skip_integration = [
        (backend, "No database type specified"),
        (url, "No LimeSurvey URL specified"),
        (username, "No LimeSurvey username specified"),
        (password, "No LimeSurvey password specified"),
    ]

    for item in items:
        if backend == "mysql" and "xfail_mysql" in item.keywords:
            item.add_marker(xfail_mysql)

        if "integration_test" in item.keywords:
            for value, reason in skip_integration:
                _add_integration_skip(item, value, reason)


def pytest_report_header() -> list[str]:
    """Return a list of strings to be displayed in the header of the report."""
    env_vars = [
        f"{key}: {value}"
        for key, value in os.environ.items()
        if key.startswith(("COVERAGE_", "NOX_"))
    ]

    dependencies = [
        f"requests: {version('requests')}",
        f"urllib3: {version('urllib3')}",
    ]

    return env_vars + dependencies


@pytest.fixture(scope="session")
def integration_url(request: pytest.FixtureRequest) -> str:
    """LimeSurvey URL."""
    return request.config.getoption("--limesurvey-url")


@pytest.fixture(scope="session")
def integration_username(request: pytest.FixtureRequest) -> str:
    """LimeSurvey username."""
    return request.config.getoption("--limesurvey-username")


@pytest.fixture(scope="session")
def integration_password(request: pytest.FixtureRequest) -> str:
    """LimeSurvey password."""
    return request.config.getoption("--limesurvey-password")


@pytest.fixture(scope="session")
def integration_mailhog_url(request: pytest.FixtureRequest) -> str:
    """MailHog URL."""
    return request.config.getoption("--mailhog-url")


class LimeSurveyMockAdapter(BaseAdapter):
    """Requests adapter that mocks LSRC2 API calls."""

    api_error_methods = ("__api_error",)
    status_error_methods = ("__status_error",)
    http_error_methods = ("__http_error",)
    ok_methods = ("__ok", "release_session_key")
    status_ok_methods = ("__status_ok", "activate_tokens", "delete_survey")

    session_key = "123456"
    status_ok: t.ClassVar[dict[str, t.Any]] = {"status": "OK"}
    rpc_interface = "json"

    ldap_session_key = "ldap-key"

    def _handle_json_response(
        self,
        method: str,
        params: list[t.Any],
        request_id: int,
    ) -> requests.Response:
        response = requests.Response()
        response.status_code = 200
        output: dict[str, t.Any] = {"result": None, "error": None, "id": request_id}

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

        response._content = json.dumps(output).encode()

        return response

    def send(
        self,
        request: requests.PreparedRequest,
        stream: bool = False,  # noqa: FBT001, FBT002
        timeout: float | tuple[float, float] | tuple[float, None] | None = None,
        verify: bool | str = True,  # noqa: FBT001, FBT002
        cert: None | bytes | str | tuple[bytes | str, bytes | str] = None,
        proxies: t.Mapping[str, str] | None = None,
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
            response._content = b"this is not json"
            return response

        return self._handle_json_response(method, params, request_id)

    def close(self) -> None:
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


@pytest.fixture(scope="session", autouse=True)
def faker_seed() -> int:
    """Set faker seed."""
    return 12345

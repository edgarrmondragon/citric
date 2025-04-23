"""pytest fixtures."""

from __future__ import annotations

import json
import os
from importlib.metadata import version
from typing import Any, ClassVar, Mapping

import pytest
import requests
from dotenv import load_dotenv
from requests.adapters import BaseAdapter

from citric.session import Session

load_dotenv()


def _from_env_var(
    env_var: str,
    default: str | None = None,
) -> str | None:
    """Get a value from an environment variable or return a default."""
    return os.environ.get(env_var, default)


def pytest_addoption(parser: pytest.Parser):
    """Add command line options to pytest."""
    parser.addoption(
        "--integration",
        action="store_true",
        help="Enable integration tests.",
    )

    parser.addoption(
        "--limesurvey-database-type",
        action="store",
        choices=["postgres", "mysql"],
        help="Database used for integration tests.",
        default=_from_env_var("LS_DATABASE_TYPE", "postgres"),
    )

    parser.addoption(
        "--limesurvey-image-tag",
        action="store",
        help="Docker image tag for integration tests.",
        default=_from_env_var("LS_IMAGE_TAG", "6-apache"),
    )

    parser.addoption(
        "--limesurvey-username",
        action="store",
        help="Username of the LimeSurvey user to test against.",
        default=_from_env_var("LS_USER", "limesurvey_user"),
    )

    parser.addoption(
        "--limesurvey-password",
        action="store",
        help="Password of the LimeSurvey user to test against.",
        default=_from_env_var("LS_PASSWORD", "limesurvey_password"),
    )

    # Use a specific git reference in LimeSurvey's repository
    parser.addoption(
        "--limesurvey-git-reference",
        action="store",
        help="Reference to a specific LimeSurvey commit.",
        default=_from_env_var("LS_REF"),
    )

    parser.addoption(
        "--limesurvey-docker-context",
        action="store",
        help="Path to the Docker context to build the LimeSurvey image.",
        default=_from_env_var(
            "LS_DOCKER_CONTEXT",
            "https://github.com/martialblog/docker-limesurvey.git#master:6.0/apache",
        ),
    )

    parser.addoption(
        "--limesurvey-dockerfile",
        action="store",
        help="Path to the Dockerfile to build the LimeSurvey image, relative to the Docker context.",  # noqa: E501
        default=_from_env_var("LS_DOCKERFILE", "Dockerfile"),
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]):
    """Modify test collection."""
    integration_enabled = config.getoption("--integration")
    backend = config.getoption("--limesurvey-database-type")

    xfail_mysql = pytest.mark.xfail(reason="This test fails on MySQL")

    for item in items:
        if backend == "mysql" and "xfail_mysql" in item.keywords:
            item.add_marker(xfail_mysql)

        if "integration_test" in item.keywords and not integration_enabled:
            marker = pytest.mark.skip(reason="Integration tests are not enabled.")
            item.add_marker(marker)


def pytest_report_header(config: pytest.Config) -> list[str]:
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

    integration = [
        f"Limesurvey database type: {config.getoption('--limesurvey-database-type')}",
        f"LimeSurvey username: {config.getoption('--limesurvey-username')}",
        f"LimeSurvey password: {config.getoption('--limesurvey-password')}",
    ]

    if config.getoption("--limesurvey-git-reference"):
        integration.extend([
            f"LimeSurvey git reference: {config.getoption('--limesurvey-git-reference')}",  # noqa: E501
            f"LimeSurvey Docker context: {config.getoption('--limesurvey-docker-context')}",  # noqa: E501
        ])
    else:
        integration.append(
            f"LimeSurvey image tag: {config.getoption('--limesurvey-image-tag')}"
        )

    return env_vars + dependencies + integration


@pytest.fixture(scope="session")
def database_type(request: pytest.FixtureRequest) -> str:
    """Database type."""
    return request.config.getoption("--limesurvey-database-type")


@pytest.fixture(scope="session")
def image_tag(request: pytest.FixtureRequest) -> str:
    """LimeSurvey URL."""
    return request.config.getoption("--limesurvey-image-tag")


@pytest.fixture(scope="session")
def integration_username(request: pytest.FixtureRequest) -> str:
    """LimeSurvey username."""
    return request.config.getoption("--limesurvey-username")


@pytest.fixture(scope="session")
def integration_password(request: pytest.FixtureRequest) -> str:
    """LimeSurvey password."""
    return request.config.getoption("--limesurvey-password")


@pytest.fixture(scope="session")
def git_reference(request: pytest.FixtureRequest) -> str:
    """LimeSurvey git reference."""
    return request.config.getoption("--limesurvey-git-reference")


@pytest.fixture(scope="session")
def docker_context(request: pytest.FixtureRequest) -> str:
    """Docker context."""
    return request.config.getoption("--limesurvey-docker-context")


@pytest.fixture(scope="session")
def dockerfile(request: pytest.FixtureRequest) -> str:
    """Dockerfile."""
    return request.config.getoption("--limesurvey-dockerfile")


class LimeSurveyMockAdapter(BaseAdapter):
    """Requests adapter that mocks LSRC2 API calls."""

    api_error_methods = ("__api_error",)
    status_error_methods = ("__status_error",)
    http_error_methods = ("__http_error",)
    ok_methods = ("__ok", "release_session_key")
    status_ok_methods = ("__status_ok", "activate_tokens", "delete_survey")

    session_key = "123456"
    status_ok: ClassVar[dict[str, Any]] = {"status": "OK"}
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

        response._content = json.dumps(output).encode()

        return response

    def send(
        self,
        request: requests.PreparedRequest,
        stream: bool = False,  # noqa: FBT001, FBT002
        timeout: float | tuple[float, float] | tuple[float, None] | None = None,
        verify: bool | str = True,  # noqa: FBT001, FBT002
        cert: bytes | str | tuple[bytes | str, bytes | str] | None = None,
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

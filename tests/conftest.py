"""pytest fixtures."""
import json
from typing import Any, Callable, Optional

import pytest
from requests_mock import Mocker

from citric import Session


@pytest.fixture(scope="session")
def url() -> str:
    """Dummy LimeSurvey RemoteControl URL."""
    return "http://example.com"


@pytest.fixture(scope="session")
def username() -> str:
    """Dummy LimeSurvey username."""
    return "limeuser"


@pytest.fixture(scope="session")
def password() -> str:
    """Dummy LimeSurvey password."""
    return "limesecret"


@pytest.fixture(scope="function")
def post_mock(url: str, requests_mock: Mocker):
    """Mock an RPC post request."""

    def internal(
        result: Any,
        error: Optional[Any] = None,
        request_id: int = 1,
        *args: Any,
        **kwargs: Any,
    ):
        """Build a fake raw RPC response."""
        payload = json.dumps({"error": error, "result": result, "id": request_id})
        requests_mock.post(url, text=payload, *args, **kwargs)

    return internal


@pytest.fixture(scope="function")
def session(url: str, username: str, password: str, post_mock: Callable[..., None]):
    """Create a LimeSurvey Session fixture."""
    post_mock("123456")
    session = Session(url, username, password)

    yield session

    post_mock("OK")
    session.close()

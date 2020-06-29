"""pytest fixtures."""
from typing import Any, Callable

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

    def internal(*args, **kwargs):
        """Execute the mock."""
        requests_mock.post(url, *args, **kwargs)

    return internal


@pytest.fixture(scope="function")
def session(url: str, username: str, password: str, post_mock: Callable[[Any], None]):
    """Create a LimeSurvey Session fixture."""
    post_mock(text='{"result":"123456","error":null,"id":1}')
    session = Session(url, username, password)

    yield session

    post_mock(text='{"result":"OK","error":null,"id":1}')
    session.close()

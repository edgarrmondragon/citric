"""pytest fixtures."""
import pytest


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

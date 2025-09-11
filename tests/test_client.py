"""Unit tests for the Python Client."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any

import pytest

from citric.client import Client
from citric.session import Session

if TYPE_CHECKING:
    from collections.abc import Generator

DUMMY_FILE_CONTENTS = b"FILE CONTENTS"


class MockSession(Session):
    """Mock RPC session with some hardcoded methods for testing."""

    def rpc(self, method: str, *params: Any) -> dict[str, Any]:
        """Process a mock RPC call."""
        return {"method": method, "params": [*params]}

    def export_timeline(self, *args: Any) -> dict[str, int]:
        """Mock submission timeline."""
        return {"2022-01-01": 4, "2022-01-02": 2}


class MockClient(Client):
    """A mock LimeSurvey client."""

    session_class = MockSession


@pytest.fixture(scope="session")
def client() -> Generator[Client, None, None]:
    """RemoteControl2 API client."""
    with MockClient("mock://lime.com", "user", "secret") as client:
        yield client


def test_export_timeline(client: MockClient):
    """Test export_timeline client method."""
    assert client.export_timeline(
        1,
        "hour",
        datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc),
    ) == {
        "2022-01-01": 4,
        "2022-01-02": 2,
    }


def test_invite_participants_unknown_status(client: MockClient):
    """Test invite_participants client method."""
    with pytest.raises(RuntimeError, match="Could not determine invitation status"):
        client.invite_participants(1)

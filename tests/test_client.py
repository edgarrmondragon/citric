"""Unit tests for the Python Client."""

from __future__ import annotations

import base64
import datetime
from typing import TYPE_CHECKING, Any, Generator

import pytest

from citric.client import Client
from citric.session import Session

if TYPE_CHECKING:
    from _pytest._py.path import LocalPath

DUMMY_FILE_CONTENTS = b"FILE CONTENTS"


class MockSession(Session):
    """Mock RPC session with some hardcoded methods for testing."""

    def rpc(self, method: str, *params: Any) -> dict[str, Any]:
        """Process a mock RPC call."""
        return {"method": method, "params": [*params]}

    def export_statistics(self, *args: Any) -> bytes:
        """Mock statistics file content."""
        return base64.b64encode(DUMMY_FILE_CONTENTS)

    def export_timeline(self, *args: Any) -> dict[str, int]:
        """Mock submission timeline."""
        return {"2022-01-01": 4, "2022-01-02": 2}


class MockClient(Client):
    """A mock LimeSurvey client."""

    session_class = MockSession


def assert_client_session_call(
    client: Client,
    method: str,
    *args: Any,
    **kwargs: Any,
):
    """Assert client makes RPC call with the right arguments.

    Args:
        client: LSRC2 API client.
        method: RPC method name.
        args: RPC method arguments.
        kwargs: Client keyword arguments.
    """
    assert getattr(client, method)(*args, **kwargs) == getattr(client.session, method)(
        *args,
        *kwargs.values(),
    )


@pytest.fixture(scope="session")
def client() -> Generator[Client, None, None]:
    """RemoteControl2 API client."""
    with MockClient("mock://lime.com", "user", "secret") as client:
        yield client


def test_get_summary(client: MockClient):
    """Test get_summary client method."""
    assert_client_session_call(client, "get_summary", 1)


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


def test_save_statistics(client: MockClient, tmpdir: LocalPath):
    """Test save_statistics and export_responses_by_token client methods."""
    filename = tmpdir / "example.html"
    client.save_statistics(filename, 1, file_format="html")
    assert filename.read_binary() == DUMMY_FILE_CONTENTS


def test_invite_participants_unknown_status(client: MockClient):
    """Test invite_participants client method."""
    with pytest.raises(RuntimeError, match="Could not determine invitation status"):
        client.invite_participants(1)

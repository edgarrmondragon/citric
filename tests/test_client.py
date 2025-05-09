"""Unit tests for the Python Client."""

from __future__ import annotations

import base64
import datetime
from typing import TYPE_CHECKING, Any, ClassVar, Generator

import pytest

from citric.client import Client
from citric.session import Session

if TYPE_CHECKING:
    from _pytest._py.path import LocalPath


NEW_GROUP_ID = 300
NEW_QUESTION_ID = 400
NEW_SURVEY_NAME = "New Survey"
DUMMY_FILE_CONTENTS = b"FILE CONTENTS"


class MockSession(Session):
    """Mock RPC session with some hardcoded methods for testing."""

    settings: ClassVar[dict[str, Any]] = {
        "defaulttheme": "mock-theme",
        "sitename": "mock-site",
        "defaultlang": "mock-lang",
        "restrictToLanguages": "en fr es",
        "versionnumber": "6.0.0",
        "dbversionnumber": 321,
    }

    def rpc(self, method: str, *params: Any) -> dict[str, Any]:
        """Process a mock RPC call."""
        return {"method": method, "params": [*params]}

    def list_questions(
        self,
        survey_id: int,
        group_id: int | None = None,
        *args: Any,
    ) -> list[dict[str, Any]]:
        """Mock questions."""
        return [
            {"title": "Q1", "qid": 1, "gid": group_id or 1, "sid": survey_id},
            {"title": "Q2", "qid": 2, "gid": group_id or 1, "sid": survey_id},
        ]

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


def test_map_response_data(client: MockClient):
    """Test question keys get mapped to LimeSurvey's internal representation."""
    question_mapping = client._get_question_mapping(1)
    mapped_responses = client._map_response_keys(
        {"Q1": "foo", "Q2": "bar", "BAZ": "qux"},
        question_mapping,
    )
    assert mapped_responses == {
        "1X1X1": "foo",
        "1X1X2": "bar",
        "BAZ": "qux",
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

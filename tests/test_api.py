"""Unit tests for the Python Client."""
import base64
import io
from pathlib import Path
from typing import Any, Dict, List

import pytest
from tempfile import TemporaryDirectory

from citric import Client, Session
from citric.client import ImportSurveyType
from citric.session import _BaseSession


class MockSession(_BaseSession):
    """Mock RPC session with some hardcoded methods for testing."""

    def import_survey(self, content: str, file_type: str = "lss") -> Dict[str, Any]:
        """Mock result from importing a survey file."""
        return {"content": base64.b64decode(content.encode()), "type": file_type}

    def list_questions(
        self, survey_id: int, group_id: int = None, *args: Any
    ) -> List[Dict[str, Any]]:
        """Mock questions."""
        return [
            {"title": "Q1", "qid": 1, "gid": group_id or 1, "sid": survey_id},
            {"title": "Q2", "qid": 2, "gid": group_id or 1, "sid": survey_id},
        ]

    def add_response(self, *args: Any) -> str:
        """Mock result from adding a response."""
        return "1"

    def export_responses(self, *args: Any) -> str:  # noqa: ANN101
        """Mock responses file content."""
        return base64.b64encode(b"FILE CONTENTS")

    def export_responses_by_token(self, *args: Any) -> str:  # noqa: ANN101
        """Mock responses file content."""
        return base64.b64encode(b"FILE CONTENTS")


@pytest.fixture(scope="module")
def session() -> MockSession:
    """A mock RPC session fixture."""
    return MockSession()


@pytest.fixture(scope="module")
def client(session: Session) -> Client:
    """RemoteControl2 API client."""
    return Client(session)


def test_activate_survey(client: Client):
    """Test activate_survey client method."""
    assert client.activate_survey(1) == client.session.activate_survey(1)


def test_activate_tokens(client: Client):
    """Test activate_tokens client method."""
    assert client.activate_tokens(1) == client.session.activate_tokens(1)


def test_delete_survey(client: Client):
    """Test activate_tokens client method."""
    assert client.delete_survey(1) == client.session.delete_survey(1)


def test_list_surveys(client: Client):
    """Test list_surveys client method."""
    assert client.list_surveys() == client.session.list_surveys(None)


def test_get_survey_properties(client: Client):
    """Test get_survey_properties client method."""
    assert client.get_survey_properties(1) == client.session.get_survey_properties(
        1, None
    )


def test_list_questions(client: Client):
    """Test list_questions client method."""
    assert client.list_questions(1) == client.session.list_questions(1)


def test_add_participants(client: Client):
    """Test add_participants client method."""
    participants = [{"firstname": "Alice"}, {"firstname": "Bob"}]
    assert client.add_participants(1, participants) == client.session.add_participants(
        1, participants, True
    )


def test_participant_properties(client: Client):
    """Test get_participant_properties client method."""
    assert client.get_participant_properties(
        1, 1
    ) == client.session.get_participant_properties(1, 1, None)


def test_list_participants(client: Client):
    """Test get_participant_properties client method."""
    assert client.list_participants(1) == client.session.list_participants(
        1, 0, 10, False, False, {}
    )


def test_import_survey(client: Client):
    """Test import_survey client method."""
    # TODO: generate this truly randomly
    random_bytes = b"1924m01'9280u '0', u'012"

    with TemporaryDirectory() as td:
        filepath = Path(td) / "survey.lss"

        with open(filepath, "wb") as f:
            f.write(random_bytes)

        assert client.import_survey(filepath) == {
            "content": random_bytes,
            "type": ImportSurveyType("lss"),
        }


def test_map_response_data(client: Client):
    """Test question keys get mapped to LimeSurvey's internal representation."""
    assert client._map_response_keys(1, {"Q1": "foo", "Q2": "bar", "BAZ": "qux"}) == {
        "1X1X1": "foo",
        "1X1X2": "bar",
        "BAZ": "qux",
    }


def test_add_responses(client: Client):
    """Test add_responses client method."""
    assert client.add_responses(1, [{"Q1": "foo"}, {"Q1": "bar"}]) == [1, 1]


def test_export_responses(client: Client):
    """Test export_responses and export_responses_by_token client methods."""
    with io.BytesIO() as fileobj:
        client.export_responses(fileobj, 1, "csv")
        fileobj.seek(0)
        assert fileobj.read() == b"FILE CONTENTS"

    with io.BytesIO() as fileobj:
        client.export_responses_by_token(fileobj, 1, "csv", 1)
        fileobj.seek(0)
        assert fileobj.read() == b"FILE CONTENTS"

"""Unit tests for the Python Client."""
import base64
import io
from pathlib import Path
from typing import Any, Dict, Generator, List

import pytest

from citric.client import _BaseClient, ImportSurveyType
from citric.session import _BaseSession


class MockSession(_BaseSession):
    """Mock RPC session with some hardcoded methods for testing."""

    settings = {
        "defaulttheme": "mock-theme",
        "sitename": "mock-site",
        "defaultlang": "mock-lang",
        "restrictToLanguages": "en fr es",
    }

    def rpc(self, method: str, *params: Any) -> Dict[str, Any]:  # noqa: ANN101
        """A mock RPC call."""
        return {"method": method, "params": [*params]}

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

    def export_responses(self, *args: Any) -> bytes:  # noqa: ANN101
        """Mock responses file content."""
        return base64.b64encode(b"FILE CONTENTS")

    def export_responses_by_token(self, *args: Any) -> bytes:  # noqa: ANN101
        """Mock responses file content."""
        return base64.b64encode(b"FILE CONTENTS")

    def get_site_settings(self, setting_name: str) -> str:  # noqa: ANN101
        """Return the setting value or an empty string."""
        return self.settings.get(setting_name, "")


class MockClient(_BaseClient):
    """A mock LimeSurvey client."""

    class ClientSession(MockSession):
        """Session implementation for this client."""


@pytest.fixture(scope="session")
def client() -> Generator[_BaseClient, None, None]:
    """RemoteControl2 API client."""
    with MockClient("mock://lime.com", "user", "secret") as client:
        yield client


def test_activate_survey(client: MockClient):
    """Test activate_survey client method."""
    assert client.activate_survey(1) == client.session.activate_survey(1)


def test_activate_tokens(client: MockClient):
    """Test activate_tokens client method."""
    assert client.activate_tokens(1) == client.session.activate_tokens(1)


def test_delete_survey(client: MockClient):
    """Test activate_tokens client method."""
    assert client.delete_survey(1) == client.session.delete_survey(1)


def test_list_surveys(client: MockClient):
    """Test list_surveys client method."""
    assert client.list_surveys() == client.session.list_surveys(None)


def test_get_response_ids(client: MockClient):
    """Test get stored response IDs from a survey."""
    assert client.get_response_ids(1, "TOKEN") == client.session.get_response_ids(
        1, "TOKEN"
    )


def test_get_survey_properties(client: MockClient):
    """Test get_survey_properties client method."""
    assert client.get_survey_properties(1) == client.session.get_survey_properties(
        1, None
    )


def test_list_questions(client: MockClient):
    """Test list_questions client method."""
    assert client.list_questions(1) == client.session.list_questions(1)


def test_add_participants(client: MockClient):
    """Test add_participants client method."""
    participants = [{"firstname": "Alice"}, {"firstname": "Bob"}]
    assert client.add_participants(1, participants) == client.session.add_participants(
        1, participants, True
    )


def test_participant_properties(client: MockClient):
    """Test get_participant_properties client method."""
    assert client.get_participant_properties(
        1, 1
    ) == client.session.get_participant_properties(1, 1, None)


def test_list_participants(client: MockClient):
    """Test get_participant_properties client method."""
    assert client.list_participants(1) == client.session.list_participants(
        1, 0, 10, False, False, {}
    )


def test_get_default_theme(client: MockClient):
    """Test get site default theme."""
    assert client.get_default_theme() == "mock-theme"


def test_get_site_name(client: MockClient):
    """Test get site name."""
    assert client.get_site_name() == "mock-site"


def test_get_default_language(client: MockClient):
    """Test get site default language."""
    assert client.get_default_language() == "mock-lang"


def test_get_available_languages(client: MockClient):
    """Test get site available languages."""
    assert client.get_available_languages() == ["en", "fr", "es"]


def test_import_survey(client: MockClient, tmp_path: Path):
    """Test import_survey client method."""
    # TODO: generate this truly randomly
    random_bytes = b"1924m01'9280u '0', u'012"

    filepath = Path(tmp_path) / "survey.lss"

    with open(filepath, "wb") as f:
        f.write(random_bytes)

    assert client.import_survey(filepath) == {
        "content": random_bytes,
        "type": ImportSurveyType("lss"),
    }


def test_map_response_data(client: MockClient):
    """Test question keys get mapped to LimeSurvey's internal representation."""
    assert client._map_response_keys(1, {"Q1": "foo", "Q2": "bar", "BAZ": "qux"}) == {
        "1X1X1": "foo",
        "1X1X2": "bar",
        "BAZ": "qux",
    }


def test_add_responses(client: MockClient):
    """Test add_responses client method."""
    assert client.add_responses(1, [{"Q1": "foo"}, {"Q1": "bar"}]) == [1, 1]


def test_export_responses(client: MockClient):
    """Test export_responses and export_responses_by_token client methods."""
    with io.BytesIO() as fileobj:
        client.export_responses(fileobj, 1, "csv")
        fileobj.seek(0)
        assert fileobj.read() == b"FILE CONTENTS"

    with io.BytesIO() as fileobj:
        client.export_responses_by_token(fileobj, 1, "csv", "123abc")
        fileobj.seek(0)
        assert fileobj.read() == b"FILE CONTENTS"

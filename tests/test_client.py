"""Unit tests for the Python Client."""

from __future__ import annotations

import base64
import datetime
import sys
import typing as t
from pathlib import Path

import pytest

from citric.client import Client
from citric.enums import ImportGroupType, ImportSurveyType, NewSurveyType
from citric.session import Session

if sys.version_info >= (3, 9):
    from random import randbytes
else:
    from random import getrandbits

    def randbytes(n: int) -> bytes:  # noqa: D103
        return getrandbits(n * 8).to_bytes(n, "little")


if t.TYPE_CHECKING:
    from _pytest._py.path import LocalPath
    from faker import Faker

    from citric import types

NEW_GROUP_ID = 300
NEW_QUESTION_ID = 400
NEW_SURVEY_NAME = "New Survey"
DUMMY_FILE_CONTENTS = b"FILE CONTENTS"


class MockSession(Session):
    """Mock RPC session with some hardcoded methods for testing."""

    settings: t.ClassVar[dict[str, t.Any]] = {
        "defaulttheme": "mock-theme",
        "sitename": "mock-site",
        "defaultlang": "mock-lang",
        "restrictToLanguages": "en fr es",
        "versionnumber": "6.0.0",
        "dbversionnumber": 321,
    }

    def rpc(self, method: str, *params: t.Any) -> dict[str, t.Any]:
        """Process a mock RPC call."""
        return {"method": method, "params": [*params]}

    def import_group(
        self,
        survey_id: int,
        content: str,
        file_type: str = "lsq",
        new_name: str | None = None,
        new_description: str | None = None,
    ) -> int:
        """Mock result from importing a group file."""
        return NEW_GROUP_ID

    def import_question(
        self,
        survey_id: int,
        group_id: int,
        content: str,
        file_type: str = "lsq",
        mandatory: str = "N",
        new_title: str | None = None,
        new_text: str | None = None,
        new_help: str | None = None,
    ) -> int:
        """Mock result from importing a question file."""
        return NEW_QUESTION_ID

    def import_survey(
        self,
        content: str,
        file_type: str = "lss",
        survey_name: str | None = None,
        survey_id: int | None = None,
    ) -> dict[str, t.Any]:
        """Mock result from importing a survey file."""
        return {"content": base64.b64decode(content.encode()), "type": file_type}

    def list_questions(
        self,
        survey_id: int,
        group_id: int | None = None,
        *args: t.Any,
    ) -> list[dict[str, t.Any]]:
        """Mock questions."""
        return [
            {"title": "Q1", "qid": 1, "gid": group_id or 1, "sid": survey_id},
            {"title": "Q2", "qid": 2, "gid": group_id or 1, "sid": survey_id},
        ]

    def add_response(self, *args: t.Any) -> str:
        """Mock result from adding a response."""
        return "1"

    def export_responses(self, *args: t.Any) -> bytes:
        """Mock responses file content."""
        return base64.b64encode(DUMMY_FILE_CONTENTS)

    def export_responses_by_token(self, *args: t.Any) -> bytes:
        """Mock responses file content."""
        return base64.b64encode(DUMMY_FILE_CONTENTS)

    def export_statistics(self, *args: t.Any) -> bytes:
        """Mock statistics file content."""
        return base64.b64encode(DUMMY_FILE_CONTENTS)

    def export_timeline(self, *args: t.Any) -> dict[str, int]:
        """Mock submission timeline."""
        return {"2022-01-01": 4, "2022-01-02": 2}

    def get_site_settings(self, setting_name: str) -> str:
        """Return the setting value or an empty string."""
        return self.settings.get(setting_name, "")

    def get_uploaded_files(self, *args: t.Any) -> dict[str, dict[str, t.Any]]:
        """Return uploaded files fake metadata."""
        return {
            "1234": {
                "meta": {
                    "title": "one",
                    "comment": "File One",
                    "name": "file1.txt",
                    "filename": "1234",
                    "size": 48.046,
                    "ext": "txt",
                    "question": {"title": "G01Q01", "qid": 1},
                    "index": 0,
                },
                "content": base64.b64encode(b"content-1").decode(),
            },
            "5678": {
                "meta": {
                    "title": "two",
                    "comment": "File Two",
                    "size": "581.044921875",
                    "name": "file2.txt",
                    "filename": "5678",
                    "ext": "txt",
                    "question": {"title": "G01Q01", "qid": 1},
                    "index": 1,
                },
                "content": base64.b64encode(b"content-2").decode(),
            },
        }

    def invite_participants(  # noqa: D102
        self,
        survey_id: int,
        token_ids: list[int] | None,
        strategy: str,
    ):
        return "OK"


class MockClient(Client):
    """A mock LimeSurvey client."""

    session_class = MockSession


def assert_client_session_call(
    client: Client,
    method: str,
    *args: t.Any,
    **kwargs: t.Any,
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
def client() -> t.Generator[Client, None, None]:
    """RemoteControl2 API client."""
    with MockClient("mock://lime.com", "user", "secret") as client:
        yield client


def test_activate_survey(client: MockClient):
    """Test activate_survey client method."""
    assert_client_session_call(
        client,
        "activate_survey",
        1,
        user_activation_settings=None,
    )


def test_activate_tokens(client: MockClient):
    """Test activate_tokens client method."""
    assert_client_session_call(client, "activate_tokens", 1, [])


def test_add_group(client: MockClient):
    """Test add_group client method."""
    assert_client_session_call(
        client,
        "add_group",
        1,
        "My Group",
        "A very simple question group",
    )


def test_add_language(client: MockClient):
    """Test add_language client method."""
    assert_client_session_call(client, "add_language", 1, "ru")


def test_add_survey(client: MockClient):
    """Test add_survey client method."""
    assert_client_session_call(
        client,
        "add_survey",
        1,
        NEW_SURVEY_NAME,
        "en",
        NewSurveyType.ALL_ON_ONE_PAGE,
    )

    with pytest.raises(ValueError, match="'NOT VALID' is not a valid NewSurveyType"):
        assert_client_session_call(
            client,
            "add_survey",
            1,
            NEW_SURVEY_NAME,
            "en",
            "NOT VALID",
        )


def test_copy_survey(client: MockClient):
    """Test copy_survey client method."""
    assert_client_session_call(
        client,
        "copy_survey",
        1,
        NEW_SURVEY_NAME,
        destination_survey_id=None,
    )


def test_delete_group(client: MockClient):
    """Test delete_group client method."""
    assert_client_session_call(client, "delete_group", 1, 10)


def test_delete_language(client: MockClient):
    """Test delete_language client method."""
    assert_client_session_call(client, "delete_language", 1, "ru")


def test_delete_question(client: MockClient):
    """Test delete_question client method."""
    assert_client_session_call(client, "delete_question", 400)


def test_delete_response(client: MockClient):
    """Test delete_response client method."""
    assert_client_session_call(client, "delete_response", 1, 1)


def test_delete_survey(client: MockClient):
    """Test delete_survey client method."""
    assert_client_session_call(client, "delete_survey", 1)


def test_list_groups(client: MockClient):
    """Test list_groups client method."""
    assert_client_session_call(client, "list_groups", 1, "en")


def test_list_surveys(client: MockClient):
    """Test list_surveys client method."""
    assert_client_session_call(client, "list_surveys", None)


def test_list_survey_groups(client: MockClient):
    """Test list_survey_groups client method."""
    assert_client_session_call(client, "list_survey_groups", None)


def test_get_group_properties(client: MockClient):
    """Test get_group_properties client method."""
    assert_client_session_call(
        client,
        "get_group_properties",
        123,
        settings=["gid"],
        language="es",
    )


def test_get_language_properties(client: MockClient):
    """Test get_language_properties client method."""
    assert_client_session_call(
        client,
        "get_language_properties",
        123,
        settings=["surveyls_email_register_subj"],
        language="es",
    )


def test_get_question_properties(client: MockClient):
    """Test get_question_properties client method."""
    assert_client_session_call(
        client,
        "get_question_properties",
        123,
        settings=["type"],
        language="es",
    )


def test_get_response_ids(client: MockClient):
    """Test get stored response IDs from a survey."""
    assert_client_session_call(client, "get_response_ids", 1, "TOKEN")


def test_get_summary(client: MockClient):
    """Test get_summary client method."""
    assert_client_session_call(client, "get_summary", 1)


def test_get_survey_properties(client: MockClient):
    """Test get_survey_properties client method."""
    assert_client_session_call(client, "get_survey_properties", 1, None)


def test_list_users(client: MockClient):
    """Test list_users client method."""
    assert_client_session_call(client, "list_users")


def test_list_questions(client: MockClient):
    """Test list_questions client method."""
    assert_client_session_call(client, "list_questions", 1)


def test_add_participants(client: MockClient, faker: Faker):
    """Test add_participants client method."""
    participants = [
        {"firstname": faker.first_name()},
        {"firstname": faker.first_name()},
    ]
    assert_client_session_call(
        client,
        "add_participants",
        1,
        participant_data=participants,
        create_tokens=True,
    )


def test_delete_participants(client: MockClient):
    """Test delete_participants client method."""
    participants = [1, 2, 3]
    assert_client_session_call(client, "delete_participants", 1, participants)


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


def test_participant_properties(client: MockClient):
    """Test get_participant_properties client method."""
    assert_client_session_call(client, "get_participant_properties", 1, 1, None)


def test_list_participants(client: MockClient):
    """Test get_participant_properties client method."""
    assert_client_session_call(
        client,
        "list_participants",
        1,
        start=0,
        limit=10,
        unused=False,
        attributes=False,
        conditions={},
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


def test_get_server_version(client: MockClient):
    """Test get server version."""
    assert client.get_server_version() == "6.0.0"


def test_get_database_version(client: MockClient):
    """Test get database version."""
    assert client.get_db_version() == 321


def test_import_group(client: MockClient, tmp_path: Path):
    """Test import_group client method."""
    random_bytes = randbytes(100)

    filepath = Path(tmp_path) / "group.lsq"

    with Path(filepath).open("wb") as f:
        f.write(random_bytes)

    with Path(filepath).open("rb") as f:
        assert client.import_group(f, 100, ImportGroupType.LSG) == NEW_GROUP_ID


def test_import_question(client: MockClient, tmp_path: Path):
    """Test import_question client method."""
    random_bytes = randbytes(100)

    filepath = Path(tmp_path) / "question.lsq"

    with Path(filepath).open("wb") as f:
        f.write(random_bytes)

    with Path(filepath).open("rb") as f:
        assert client.import_question(f, 100, 1) == NEW_QUESTION_ID


def test_import_survey(client: MockClient, tmp_path: Path):
    """Test import_survey client method."""
    random_bytes = randbytes(100)

    filepath = Path(tmp_path) / "survey.lss"

    with Path(filepath).open("wb") as f:
        f.write(random_bytes)

    with Path(filepath).open("rb") as f:
        assert client.import_survey(f) == {
            "content": random_bytes,
            "type": ImportSurveyType.LSS,
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


def test_add_responses(client: MockClient):
    """Test add_responses client method."""
    assert client.add_responses(1, [{"Q1": "foo"}, {"Q1": "bar"}]) == [1, 1]


def test_save_responses(client: MockClient, tmpdir: LocalPath):
    """Test export_responses and export_responses_by_token client methods."""
    filename = tmpdir / "responses.csv"
    client.save_responses(filename, 1, file_format="csv")
    assert filename.read_binary() == DUMMY_FILE_CONTENTS

    filename_token = tmpdir / "responses_token.csv"
    client.save_responses(filename_token, 1, token="123abc", file_format="csv")
    assert filename_token.read_binary() == DUMMY_FILE_CONTENTS


def test_save_statistics(client: MockClient, tmpdir: LocalPath):
    """Test save_statistics and export_responses_by_token client methods."""
    filename = tmpdir / "example.html"
    client.save_statistics(filename, 1, file_format="html")
    assert filename.read_binary() == DUMMY_FILE_CONTENTS


def test_download_files(client: MockClient, tmp_path: Path):
    """Test files are downloaded correctly."""
    expected = {tmp_path / "1234", tmp_path / "5678"}
    paths = client.download_files(tmp_path, 1, "TOKEN")

    assert set(paths) == expected
    assert paths[0].read_text() == "content-1"
    assert paths[1].read_text() == "content-2"


def test_set_group_properties(client: MockClient):
    """Test set_group_properties client method."""
    props: types.GroupProperties = {"group_name": "foo"}
    assert client.set_group_properties(
        1,
        **props,
    ) == client.session.set_group_properties(1, props)


def test_set_language_properties(client: MockClient):
    """Test set_language_properties client method."""
    props: types.LanguageProperties = {"surveyls_title": "foo"}
    assert client.set_language_properties(
        1,
        language="en",
        **props,
    ) == client.session.set_language_properties(1, props, "en")


def test_set_participant_properties(client: MockClient):
    """Test set_participant_properties client method."""
    token_data = {"name": "Bob"}
    assert client.set_participant_properties(
        1,
        123,
        **token_data,
    ) == client.session.set_participant_properties(1, 123, token_data)


def test_set_question_properties(client: MockClient):
    """Test set_question_properties client method."""
    props: types.QuestionProperties = {"title": "foo", "mandatory": "Y", "type": "text"}
    assert client.set_question_properties(
        1,
        language="en",
        **props,
    ) == client.session.set_question_properties(1, props, "en")


def test_set_quota_properties(client: MockClient):
    """Test set_quota_properties client method."""
    props: types.QuotaProperties = {"name": "foo", "qlimit": 150, "action": 1}
    assert client.set_quota_properties(
        1,
        **props,
    ) == client.session.set_quota_properties(1, props)


def test_set_survey_properties(client: MockClient, faker: Faker):
    """Test set_survey_properties client method."""
    props: types.SurveyProperties = {
        "allowsave": "Y",
        "ipanonymize": "Y",
        "emailnotificationto": faker.email(),
    }
    assert client.set_survey_properties(
        1,
        **props,
    ) == client.session.set_survey_properties(1, props)


def test_invite_participants_unknown_status(client: MockClient):
    """Test invite_participants client method."""
    with pytest.raises(RuntimeError, match="Could not determine invitation status"):
        client.invite_participants(1)

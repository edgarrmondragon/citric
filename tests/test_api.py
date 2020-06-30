"""Unit tests for the Python Client."""
import base64
import io
from pathlib import Path
from typing import Callable

import pytest
from requests_mock import Mocker

from citric import Client, Session
from citric.exceptions import LimeSurveyStatusError


@pytest.fixture(scope="function")
def client(session: Session) -> Client:
    """RemoteControl2 API client."""
    return Client(session)


def test_status_ok(client: Client, post_mock: Callable[..., None]):
    """Test methods that response only with OK status."""
    post_mock({"status": "OK"})
    assert client.activate_survey(1) == {"status": "OK"}

    post_mock({"status": "OK"})
    assert client.activate_tokens(1) == {"status": "OK"}

    post_mock({"status": "OK"})
    assert client.delete_survey(1) == {"status": "OK"}


def test_side_effects(url: str, client: Client, post_mock: Callable[..., None]):
    """Test methods with side effects."""
    post_mock(31415)
    survey_id = client.import_survey(Path("./examples/survey.lss"))
    assert survey_id == 31415

    post_mock([{"sid": 31415}])
    assert client.list_surveys() == [{"sid": 31415}]

    post_mock({"active": "Y"})
    assert client.get_survey_properties(survey_id, ["active"]) == {"active": "Y"}

    post_mock([{"qid": 27182}])
    assert client.list_questions(survey_id) == [{"qid": 27182}]

    post_mock({"status": "surveytablecreation"})
    with pytest.raises(LimeSurveyStatusError, match="surveytablecreation"):
        client.activate_survey(survey_id)

    post_mock([{"firstname": "Alice"}, {"firstname": "Bob"}])
    participants = [{"firstname": "Alice"}, {"firstname": "Bob"}]
    assert client.add_participants(survey_id, participants) == [
        {"firstname": "Alice"},
        {"firstname": "Bob"},
    ]

    post_mock(base64.b64encode(b"FILE CONTENTS").decode())
    with io.BytesIO() as fileobj:
        client.export_responses(fileobj, survey_id, "csv")
        fileobj.seek(0)
        assert fileobj.read() == b"FILE CONTENTS"

    post_mock(base64.b64encode(b"FILE CONTENTS").decode())
    with io.BytesIO() as fileobj:
        client.export_responses_by_token(fileobj, survey_id, "csv", "t0001")
        fileobj.seek(0)
        assert fileobj.read() == b"FILE CONTENTS"

    post_mock({"prop": 1})
    assert client.get_participant_properties(survey_id, {"prop": 1}) == {"prop": 1}

    post_mock({"prop": 1})
    assert client.list_participants(survey_id) == {"prop": 1}


def test_add_multiple_responses(url: str, client: Client, requests_mock: Mocker):
    """Test response creation calls."""
    requests_mock.post(
        url,
        [
            {
                "json": {
                    "result": [
                        {"title": "Q1", "sid": 1, "gid": 1, "qid": 1},
                        {"title": "Q2", "sid": 1, "gid": 1, "qid": 2},
                    ],
                    "error": None,
                    "id": 1,
                },
            },
            {"json": {"result": 1, "error": None, "id": 1}},
        ],
    )
    assert client.add_responses(1, [{"Q1": "first", "Q2": "second"}]) == [1]

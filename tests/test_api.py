"""Unit tests for the Python API."""
from typing import Callable

import base64
import io
from pathlib import Path

import pytest

from citric import API, Session
from citric.exceptions import LimeSurveyStatusError


@pytest.fixture(scope="function")
def api(session: Session) -> API:
    """RemoteControl2 API."""
    return API(session)


def test_status_ok(api: API, post_mock: Callable[..., None]):
    """Test methods that response only with OK status."""
    post_mock(text='{"result":{"status":"OK"},"error":null,"id":1}')
    assert api.activate_survey(1) == {"status": "OK"}

    post_mock(text='{"result":{"status":"OK"},"error":null,"id":1}')
    assert api.activate_tokens(1) == {"status": "OK"}

    post_mock(text='{"result":{"status":"OK"},"error":null,"id":1}')
    assert api.delete_survey(1) == {"status": "OK"}


def test_side_effects(url: str, api: API, post_mock: Callable[..., None]):
    """Test methods with side effects."""
    post_mock(text='{"result":31415,"error":null,"id":1}')
    survey_id = api.import_survey(Path("./examples/survey.lss"))
    assert survey_id == 31415

    post_mock(text='{"result":[{"sid":31415}],"error":null,"id":1}')
    assert api.list_surveys() == [{"sid": 31415}]

    post_mock(text='{"result":{"active":"Y"},"error":null,"id":1}')
    assert api.get_survey_properties(survey_id, ["active"]) == {"active": "Y"}

    post_mock(text='{"result":[{"qid":27182}],"error":null,"id":1}')
    assert api.list_questions(survey_id) == [{"qid": 27182}]

    post_mock(text='{"result":{"status":"surveytablecreation"},"error":null,"id":1}')
    with pytest.raises(LimeSurveyStatusError, match="surveytablecreation"):
        api.activate_survey(survey_id)

    post_mock(
        json={
            "result": [{"firstname": "Alice"}, {"firstname": "Bob"}],
            "error": None,
            "id": 1,
        },
    )
    participants = [{"firstname": "Alice"}, {"firstname": "Bob"}]
    assert api.add_participants(survey_id, participants) == [
        {"firstname": "Alice"},
        {"firstname": "Bob"},
    ]

    post_mock(
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
        ]
    )
    assert api.add_responses(survey_id, [{"Q1": "first", "Q2": "second"}]) == [1]

    post_mock(
        json={
            "result": base64.b64encode(b"FILE CONTENTS").decode(),
            "error": None,
            "id": 1,
        }
    )
    with io.BytesIO() as fileobj:
        api.export_responses(fileobj, survey_id, "csv")
        fileobj.seek(0)
        assert fileobj.read() == b"FILE CONTENTS"

    post_mock(
        json={
            "result": base64.b64encode(b"FILE CONTENTS").decode(),
            "error": None,
            "id": 1,
        }
    )
    with io.BytesIO() as fileobj:
        api.export_responses_by_token(fileobj, survey_id, "csv", "t0001")
        fileobj.seek(0)
        assert fileobj.read() == b"FILE CONTENTS"

    post_mock(text='{"result":{"prop":1},"error":null,"id":1}')
    assert api.get_participant_properties(survey_id, {"prop": 1}) == {"prop": 1}

    post_mock(text='{"result":{"prop":1},"error":null,"id":1}')
    assert api.list_participants(survey_id) == {"prop": 1}

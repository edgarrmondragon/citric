"""Integration tests for Python API."""
from pathlib import Path

import csv
import io
import pytest

from citric import API, Session
from citric.exceptions import LimeSurveyStatusError

LS_URL = "http://localhost:8001/index.php/admin/remotecontrol"
LS_USER = "iamadmin"
LS_PW = "secret"
STATUS_OK = {"status": "OK"}
STATUS_ERROR = "LimeSurveyStatusError: %s"


@pytest.fixture(scope="session")
def api() -> API:
    """RemoteControl2 API."""
    session = Session(LS_URL, LS_USER, LS_PW)
    api = API(session)

    yield api

    try:
        for survey in api.list_surveys():
            api.delete_survey(survey["sid"])
    except LimeSurveyStatusError:
        pass

    session.close()


@pytest.fixture(scope="function")
def survey_id(api: API) -> int:
    """Import a survey from a file and return its ID."""
    survey_id = api.import_survey(Path("./examples/survey.lss"))

    yield survey_id

    api.delete_survey(survey_id)


def test_activate_survey(api: API, survey_id: int):
    """Test whether the survey gets activated."""
    properties_before = api.get_survey_properties(survey_id, ["active"])
    assert properties_before["active"] == "N"

    result = api.activate_survey(survey_id)
    assert result["status"] == "OK"

    properties_after = api.get_survey_properties(survey_id, ["active"])
    assert properties_after["active"] == "Y"


def test_activate_tokens(api: API, survey_id: int):
    """Test whether the participants table gets activated."""
    api.activate_survey(survey_id)

    with pytest.raises(LimeSurveyStatusError, match="No survey participants table"):
        api.list_participants(survey_id)

    api.activate_tokens(survey_id)

    with pytest.raises(LimeSurveyStatusError, match="No survey participants found"):
        api.list_participants(survey_id)


def test_participants(api: API, survey_id: int):
    """Test adding participants."""
    api.activate_survey(survey_id)
    api.activate_tokens(survey_id)

    data = [
        {"email": "john@example.com", "firstname": "John", "lastname": "Doe"},
        {"email": "jane@example.com", "firstname": "Jane", "lastname": "Doe"},
    ]

    added = api.add_participants(survey_id, data)
    for p, d in zip(added, data):
        assert p["email"] == d["email"]
        assert p["firstname"] == d["firstname"]
        assert p["lastname"] == d["lastname"]

    participants = api.list_participants(survey_id)
    for p, d in zip(participants, data):
        assert p["participant_info"]["email"] == d["email"]
        assert p["participant_info"]["firstname"] == d["firstname"]
        assert p["participant_info"]["lastname"] == d["lastname"]

    for p, d in zip(added, data):
        properties = api.get_participant_properties(survey_id, p["tid"])
        assert properties["email"] == d["email"]
        assert properties["firstname"] == d["firstname"]
        assert properties["lastname"] == d["lastname"]


def test_responses(api: API, survey_id: int):
    """Test adding and exporting responses."""
    api.activate_survey(survey_id)
    api.activate_tokens(survey_id)

    data = [
        {"G01Q01": "Long text 1", "G01Q02": "1", "token": "T00000"},
        {"G01Q01": "Long text 2", "G01Q02": "5", "token": "T00001"},
        {"G01Q01": "Long text 3", "G01Q02": None, "token": "T00002"},
    ]

    result = api.add_responses(survey_id, data)
    assert result == ["1", "2", "3"]

    with io.BytesIO() as file, io.TextIOWrapper(file, encoding="utf-8-sig") as textfile:
        api.export_responses(file, survey_id, "csv")
        file.seek(0)
        reader = csv.DictReader(textfile, delimiter=";")
        for i, row in enumerate(reader):
            assert row["G01Q01"] == (data[i]["G01Q01"] or "")
            assert row["G01Q02"] == (data[i]["G01Q02"] or "")
            assert row["token"] == (data[i]["token"] or "")
        file.seek(0)

        api.export_responses_by_token(file, survey_id, "csv", "T00002")
        file.seek(0)
        reader = csv.DictReader(textfile, delimiter=";")
        row = next(reader)
        assert row["G01Q01"] == "Long text 3"
        assert row["G01Q02"] == ""
        assert row["token"] == "T00002"

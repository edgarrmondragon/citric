"""Integration tests for Python client."""

from __future__ import annotations

import csv
import io
import os
from typing import Any, Generator

import psycopg2
import pytest

import citric
from citric import enums
from citric.exceptions import LimeSurveyStatusError

LS_USER = "iamadmin"
LS_PW = "secret"

DB_URI = os.getenv("DB_URI")


@pytest.fixture(scope="module", autouse=True)
def enable_json_rpc():
    """Enable JSON RPC interface for integration tests."""
    sql = """INSERT INTO lime_settings_global (
        stg_name,
        stg_value
    )
    VALUES ('RPCInterface', 'json')
    ON CONFLICT(stg_name) DO UPDATE
    SET stg_value=EXCLUDED.stg_value;
    """

    with psycopg2.connect(DB_URI) as conn, conn.cursor() as curs:
        curs.execute(sql)
        conn.commit()


@pytest.fixture(scope="session")
def url() -> str:
    """Get LimeSurvey RC URL."""
    return os.environ["LIMESURVEY_URL"]


@pytest.fixture(scope="module")
def client(url: str) -> Generator[citric.Client, None, None]:
    """RemoteControl2 API client."""
    client = citric.Client(url, LS_USER, LS_PW)

    yield client

    try:
        for survey in client.list_surveys():
            client.delete_survey(survey["sid"])
    except LimeSurveyStatusError:
        pass

    client.close()


@pytest.fixture(scope="function")
def survey_id(client: citric.Client) -> Generator[int, None, None]:
    """Import a survey from a file and return its ID."""
    with open("./examples/survey.lss", "rb") as f:
        survey_id = client.import_survey(f, survey_id=98765)

    yield survey_id

    client.delete_survey(survey_id)


@pytest.mark.integration_test
def test_language(client: citric.Client, survey_id: int):
    """Test adding a new language to a survey."""
    # Add a new language
    client.add_language(survey_id, "es")
    client.add_language(survey_id, "ru")

    survey_props = client.get_survey_properties(survey_id)
    assert survey_props["additional_languages"] == "es ru"

    # Get language properties
    language_props = client.get_language_properties(survey_id, language="es")
    assert language_props["surveyls_email_register_subj"] is not None
    assert language_props["surveyls_email_invite"] is not None

    # Update language properties
    new_confirmation = "Thank you for participating!"
    response = client.set_language_properties(
        survey_id,
        language="es",
        surveyls_email_confirm=new_confirmation,
    )
    assert response == {"status": "OK", "surveyls_email_confirm": True}

    new_props = client.get_language_properties(
        survey_id,
        language="es",
        settings=["surveyls_email_confirm"],
    )
    assert new_props["surveyls_email_confirm"] == new_confirmation


@pytest.mark.integration_test
def test_add_survey(client: citric.Client):
    """Test adding a new survey to a survey."""
    survey_id = client.add_survey(
        5555,
        "New Survey",
        "es",
        enums.NewSurveyType.GROUP_BY_GROUP,
    )

    survey_props = client.get_survey_properties(survey_id)
    assert survey_props["language"] == "es"
    assert survey_props["format"] == enums.NewSurveyType.GROUP_BY_GROUP

    matched = next(s for s in client.list_surveys() if s["sid"] == survey_id)
    assert matched["surveyls_title"] == "New Survey"


@pytest.mark.integration_test
def test_import_group(client: citric.Client, survey_id: int):
    """Test importing a group from an lsg file."""
    with open("./examples/group.lsg", "rb") as f:
        group_id = client.import_group(f, survey_id)

    group_props = client.get_group_properties(group_id)
    assert group_props["gid"] == group_id
    assert group_props["group_name"] == "First Group"
    assert group_props["description"] == "<p>A new group</p>"

    questions = sorted(
        client.list_questions(survey_id, group_id),
        key=lambda q: q["qid"],
    )

    assert questions[0]["question"] == "<p><strong>First question</p>"
    assert questions[1]["question"] == "<p><strong>Second question</p>"


@pytest.mark.integration_test
def test_import_question(client: citric.Client, survey_id: int):
    """Test importing a question from an lsq file."""
    group_id = client.add_group(survey_id, "Test Group")

    with open("./examples/free_text.lsq", "rb") as f:
        question_id = client.import_question(f, survey_id, group_id)

    props = client.get_question_properties(question_id)
    assert props["gid"] == group_id
    assert props["qid"] == question_id
    assert props["sid"] == survey_id
    assert props["title"] == "FREETEXTEXAMPLE"


@pytest.mark.integration_test
def test_activate_survey(client: citric.Client, survey_id: int):
    """Test whether the survey gets activated."""
    properties_before = client.get_survey_properties(survey_id, ["active"])
    assert properties_before["active"] == "N"

    result = client.activate_survey(survey_id)
    assert result["status"] == "OK"

    properties_after = client.get_survey_properties(survey_id, ["active"])
    assert properties_after["active"] == "Y"


@pytest.mark.integration_test
def test_activate_tokens(client: citric.Client, survey_id: int):
    """Test whether the participants table gets activated."""
    client.activate_survey(survey_id)

    with pytest.raises(LimeSurveyStatusError, match="No survey participants table"):
        client.list_participants(survey_id)

    client.activate_tokens(survey_id)

    with pytest.raises(LimeSurveyStatusError, match="No survey participants found"):
        client.list_participants(survey_id)


@pytest.mark.integration_test
def test_participants(client: citric.Client, survey_id: int):
    """Test adding participants."""
    client.activate_survey(survey_id)
    client.activate_tokens(survey_id)

    data = [
        {"email": "john@example.com", "firstname": "John", "lastname": "Doe"},
        {"email": "jane@example.com", "firstname": "Jane", "lastname": "Doe"},
    ]

    added = client.add_participants(survey_id, data)
    for p, d in zip(added, data):
        assert p["email"] == d["email"]
        assert p["firstname"] == d["firstname"]
        assert p["lastname"] == d["lastname"]

    participants = client.list_participants(survey_id)
    for p, d in zip(participants, data):
        assert p["participant_info"]["email"] == d["email"]
        assert p["participant_info"]["firstname"] == d["firstname"]
        assert p["participant_info"]["lastname"] == d["lastname"]

    for p, d in zip(added, data):
        properties = client.get_participant_properties(survey_id, p["tid"])
        assert properties["email"] == d["email"]
        assert properties["firstname"] == d["firstname"]
        assert properties["lastname"] == d["lastname"]


@pytest.mark.integration_test
def test_responses(client: citric.Client, survey_id: int):
    """Test adding and exporting responses."""
    client.activate_survey(survey_id)
    client.activate_tokens(survey_id)

    data: list[dict[str, Any]]
    data = [
        {"G01Q01": "Long text 1", "G01Q02": "1", "token": "T00000"},
        {"G01Q01": "Long text 2", "G01Q02": "5", "token": "T00001"},
        {"G01Q01": "Long text 3", "G01Q02": None, "token": "T00002"},
    ]

    result = client.add_responses(survey_id, data)
    assert result == [1, 2, 3]

    with io.BytesIO() as file, io.TextIOWrapper(file, encoding="utf-8-sig") as textfile:
        file.write(client.export_responses(survey_id, file_format="csv"))
        file.seek(0)
        reader = csv.DictReader(textfile, delimiter=";")
        for i, row in enumerate(reader):
            assert row["G01Q01"] == (data[i]["G01Q01"] or "")
            assert row["G01Q02"] == (data[i]["G01Q02"] or "")
            assert row["token"] == (data[i]["token"] or "")
        file.seek(0)

        file.write(
            client.export_responses(survey_id, token="T00002", file_format="csv")
        )
        file.seek(0)
        reader = csv.DictReader(textfile, delimiter=";")
        row = next(reader)
        assert row["G01Q01"] == "Long text 3"
        assert row["G01Q02"] == ""
        assert row["token"] == "T00002"

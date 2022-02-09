"""Integration tests for Python client."""

from __future__ import annotations

import csv
import io
import os
from pathlib import Path
from typing import Any, Generator
from urllib.parse import quote

import pytest

import citric
from citric import enums
from citric.exceptions import LimeSurveyStatusError

LS_USER = "iamadmin"
LS_PW = "secret"


@pytest.fixture(scope="session")
def db_uri() -> str:
    """Get LimeSurvey database URI."""
    return os.environ.get(
        "DB_URI",
        "postgresql://limesurvey:secret@localhost:5432/limesurvey",
    )


@pytest.fixture(scope="module", autouse=True)
def enable_json_rpc(db_uri: str):
    """Enable JSON RPC interface for integration tests."""
    sql = """INSERT INTO lime_settings_global (
        stg_name,
        stg_value
    )
    VALUES ('RPCInterface', 'json')
    ON CONFLICT(stg_name) DO UPDATE
    SET stg_value=EXCLUDED.stg_value;
    """
    import psycopg2

    with psycopg2.connect(db_uri) as conn, conn.cursor() as curs:
        curs.execute(sql)
        conn.commit()


@pytest.fixture(scope="session")
def url() -> str:
    """Get LimeSurvey RC URL."""
    return os.environ.get(
        "LIMESURVEY_URL",
        "http://localhost:8001/index.php/admin/remotecontrol",
    )


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
    """Test language methods."""
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

    # Delete language
    response = client.delete_language(survey_id, "ru")
    assert response["status"] == "OK"

    props_after_delete_language = client.get_survey_properties(survey_id)
    assert props_after_delete_language["additional_languages"] == "es"


@pytest.mark.integration_test
def test_survey(client: citric.Client):
    """Test survey methods."""
    # Add a new survey
    survey_id = client.add_survey(
        5555,
        "New Survey",
        "es",
        enums.NewSurveyType.GROUP_BY_GROUP,
    )

    # Get survey properties
    survey_props = client.get_survey_properties(survey_id)
    assert survey_props["language"] == "es"
    assert survey_props["format"] == enums.NewSurveyType.GROUP_BY_GROUP

    matched = next(s for s in client.list_surveys() if s["sid"] == survey_id)
    assert matched["surveyls_title"] == "New Survey"

    # Update survey properties
    response = client.set_survey_properties(
        survey_id,
        format=enums.NewSurveyType.ALL_ON_ONE_PAGE,
    )
    assert response == {"format": True}

    new_props = client.get_survey_properties(survey_id, properties=["format"])
    assert new_props["format"] == enums.NewSurveyType.ALL_ON_ONE_PAGE


@pytest.mark.integration_test
def test_group(client: citric.Client, survey_id: int):
    """Test group methods."""
    # Import a group
    with open("./examples/group.lsg", "rb") as f:
        group_id = client.import_group(f, survey_id)

    # Get group properties
    group_props = client.get_group_properties(group_id)
    assert group_props["gid"] == group_id
    assert group_props["group_name"] == "First Group"
    assert group_props["description"] == "<p>A new group</p>"
    assert group_props["group_order"] == 3

    questions = sorted(
        client.list_questions(survey_id, group_id),
        key=lambda q: q["qid"],
    )

    assert questions[0]["question"] == "<p><strong>First question</p>"
    assert questions[1]["question"] == "<p><strong>Second question</p>"

    # Update group properties
    response = client.set_group_properties(group_id, group_order=1)
    assert response == {"group_order": True}

    new_props = client.get_group_properties(group_id, settings=["group_order"])
    assert new_props["group_order"] == 1


@pytest.mark.integration_test
def test_question(client: citric.Client, survey_id: int):
    """Test question methods."""
    group_id = client.add_group(survey_id, "Test Group")

    # Import a question from a lsq file
    with open("./examples/free_text.lsq", "rb") as f:
        question_id = client.import_question(f, survey_id, group_id)

    # Get question properties
    props = client.get_question_properties(question_id)
    assert props["gid"] == group_id
    assert props["qid"] == question_id
    assert props["sid"] == survey_id
    assert props["title"] == "FREETEXTEXAMPLE"

    # Update question properties
    response = client.set_question_properties(question_id, mandatory="Y")
    assert response == {"mandatory": True}

    new_props = client.get_question_properties(question_id, settings=["mandatory"])
    assert new_props["mandatory"] == "Y"

    # Delete question
    client.delete_question(question_id)

    with pytest.raises(LimeSurveyStatusError, match="No questions found"):
        client.list_questions(survey_id, group_id)


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
    """Test participants methods."""
    client.activate_survey(survey_id)
    client.activate_tokens(survey_id)

    data = [
        {"email": "john@example.com", "firstname": "John", "lastname": "Doe"},
        {"email": "jane@example.com", "firstname": "Jane", "lastname": "Doe"},
    ]

    # Add participants
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

    # Get participant properties
    for p, d in zip(added, data):
        properties = client.get_participant_properties(survey_id, p["tid"])
        assert properties["email"] == d["email"]
        assert properties["firstname"] == d["firstname"]
        assert properties["lastname"] == d["lastname"]

    # Update participant properties
    response = client.set_participant_properties(
        survey_id,
        added[0]["tid"],
        firstname="Johny",
    )
    assert response["firstname"] == "Johny"
    assert response["lastname"] == "Doe"


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


@pytest.mark.integration_test
def test_files(client: citric.Client, survey_id: int, tmp_path: Path):
    """Test uploading and downloading files from a survey."""
    filepath = tmp_path / "hello world.txt"
    filepath.write_text("Hello world!")

    client.activate_survey(survey_id)
    group = client.list_groups(survey_id)[1]
    question = client.list_questions(survey_id, group["gid"])[0]

    filename = "upload.txt"
    result = client.upload_file(
        survey_id,
        f"{survey_id}X{group['gid']}X{question['qid']}",
        filepath,
        filename=filename,
    )
    assert result["success"]
    assert result["size"] == pytest.approx(filepath.stat().st_size / 1000)
    assert result["name"] == filename
    assert result["ext"] == "txt"
    assert "filename" in result
    assert "msg" in result

    result_no_filename = client.upload_file(
        survey_id,
        f"{survey_id}X{group['gid']}X{question['qid']}",
        filepath,
    )
    assert result_no_filename["success"]
    assert result_no_filename["size"] == pytest.approx(filepath.stat().st_size / 1000)
    assert result_no_filename["name"] == quote(filepath.name)
    assert result_no_filename["ext"] == "txt"
    assert "filename" in result_no_filename
    assert "msg" in result_no_filename

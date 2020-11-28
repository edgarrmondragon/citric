"""Integration tests for Python client."""
import os
from pathlib import Path
from typing import Any, Dict, Generator, List

import csv
import io
import psycopg2
import pytest

from citric import Client
from citric.exceptions import LimeSurveyStatusError

LS_URL = os.getenv("LIMESURVEY_URL")
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


@pytest.fixture(scope="module")
def client() -> Generator[Client, None, None]:
    """RemoteControl2 API client."""
    client = Client(LS_URL, LS_USER, LS_PW)

    yield client

    try:
        for survey in client.list_surveys():
            client.delete_survey(survey["sid"])
    except LimeSurveyStatusError:
        pass

    client.close()


@pytest.fixture(scope="function")
def survey_id(client: Client) -> Generator[int, None, None]:
    """Import a survey from a file and return its ID."""
    survey_id = client.import_survey(Path("./examples/survey.lss"))

    yield survey_id

    client.delete_survey(survey_id)


@pytest.mark.integration_test
def test_activate_survey(client: Client, survey_id: int):
    """Test whether the survey gets activated."""
    properties_before = client.get_survey_properties(survey_id, ["active"])
    assert properties_before["active"] == "N"

    result = client.activate_survey(survey_id)
    assert result["status"] == "OK"

    properties_after = client.get_survey_properties(survey_id, ["active"])
    assert properties_after["active"] == "Y"


@pytest.mark.integration_test
def test_activate_tokens(client: Client, survey_id: int):
    """Test whether the participants table gets activated."""
    client.activate_survey(survey_id)

    with pytest.raises(LimeSurveyStatusError, match="No survey participants table"):
        client.list_participants(survey_id)

    client.activate_tokens(survey_id)

    with pytest.raises(LimeSurveyStatusError, match="No survey participants found"):
        client.list_participants(survey_id)


@pytest.mark.integration_test
def test_participants(client: Client, survey_id: int):
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
def test_responses(client: Client, survey_id: int):
    """Test adding and exporting responses."""
    client.activate_survey(survey_id)
    client.activate_tokens(survey_id)

    data: List[Dict[str, Any]]
    data = [
        {"G01Q01": "Long text 1", "G01Q02": "1", "token": "T00000"},
        {"G01Q01": "Long text 2", "G01Q02": "5", "token": "T00001"},
        {"G01Q01": "Long text 3", "G01Q02": None, "token": "T00002"},
    ]

    result = client.add_responses(survey_id, data)
    assert result == [1, 2, 3]

    with io.BytesIO() as file, io.TextIOWrapper(file, encoding="utf-8-sig") as textfile:
        client.export_responses(file, survey_id, "csv")
        file.seek(0)
        reader = csv.DictReader(textfile, delimiter=";")
        for i, row in enumerate(reader):
            assert row["G01Q01"] == (data[i]["G01Q01"] or "")
            assert row["G01Q02"] == (data[i]["G01Q02"] or "")
            assert row["token"] == (data[i]["token"] or "")
        file.seek(0)

        client.export_responses_by_token(file, survey_id, "csv", "T00002")
        file.seek(0)
        reader = csv.DictReader(textfile, delimiter=";")
        row = next(reader)
        assert row["G01Q01"] == "Long text 3"
        assert row["G01Q02"] == ""
        assert row["token"] == "T00002"

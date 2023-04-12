"""Integration tests for Python client."""

from __future__ import annotations

import csv
import io
import uuid
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import quote

import pytest

import citric
from citric import enums
from citric.exceptions import LimeSurveyStatusError
from citric.objects import Participant

if TYPE_CHECKING:
    from typing import Any, Generator

    from faker import Faker

NEW_SURVEY_NAME = "New Survey"


@pytest.fixture(scope="module")
def client(
    integration_url: str,
    integration_username: str,
    integration_password: str,
) -> Generator[citric.Client, None, None]:
    """RemoteControl2 API client."""
    client = citric.Client(
        integration_url,
        integration_username,
        integration_password,
    )

    yield client

    try:
        for survey in client.list_surveys(integration_username):
            client.delete_survey(survey["sid"])
    except LimeSurveyStatusError:
        pass
    finally:
        client.close()


@pytest.fixture
def survey_id(client: citric.Client) -> Generator[int, None, None]:
    """Import a survey from a file and return its ID."""
    with Path("./examples/survey.lss").open("rb") as f:
        survey_id = client.import_survey(f, survey_id=98765)

    yield survey_id

    client.delete_survey(survey_id)


@pytest.mark.integration_test
def test_fieldmap(client: citric.Client, survey_id: int):
    """Test fieldmap."""
    fieldmap = client.get_fieldmap(survey_id)
    for key, value in fieldmap.items():
        assert key == value["fieldname"]

        if value["qid"] and "_" not in key:
            assert key == "{sid}X{gid}X{qid}".format(**value)


@pytest.mark.integration_test
def test_language(client: citric.Client, survey_id: int):
    """Test language methods."""
    # Add a new language
    assert client.add_language(survey_id, "es")["status"] == "OK"
    assert client.add_language(survey_id, "ru")["status"] == "OK"

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
    delete_response = client.delete_language(survey_id, "ru")
    assert delete_response["status"] == "OK"

    props_after_delete_language = client.get_survey_properties(survey_id)
    assert props_after_delete_language["additional_languages"] == "es"


@pytest.mark.integration_test
def test_survey(client: citric.Client):
    """Test survey methods."""
    # Add a new survey
    survey_id = client.add_survey(
        5555,
        NEW_SURVEY_NAME,
        "es",
        enums.NewSurveyType.GROUP_BY_GROUP,
    )

    # Get survey properties
    survey_props = client.get_survey_properties(survey_id)
    assert survey_props["language"] == "es"
    assert survey_props["format"] == enums.NewSurveyType.GROUP_BY_GROUP

    matched = next(s for s in client.list_surveys() if int(s["sid"]) == survey_id)
    assert matched["surveyls_title"] == NEW_SURVEY_NAME

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
    with Path("./examples/group.lsg").open("rb") as f:
        group_id = client.import_group(f, survey_id)

    # Get group properties
    group_props = client.get_group_properties(group_id)
    assert int(group_props["gid"]) == group_id
    assert int(group_props["sid"]) == survey_id
    assert group_props["group_name"] == "First Group"
    assert group_props["description"] == "<p>A new group</p>"
    assert int(group_props["group_order"]) == 3

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
    assert int(new_props["group_order"]) == 1


@pytest.mark.integration_test
def test_question(client: citric.Client, survey_id: int):
    """Test question methods."""
    group_id = client.add_group(survey_id, "Test Group")

    # Import a question from a lsq file
    with Path("./examples/free_text.lsq").open("rb") as f:
        question_id = client.import_question(f, survey_id, group_id)

    # Get question properties
    props = client.get_question_properties(question_id)
    assert int(props["gid"]) == group_id
    assert int(props["qid"]) == question_id
    assert int(props["sid"]) == survey_id
    assert props["type"] == "T"
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
@pytest.mark.version("6-apache")
@pytest.mark.version("develop")
@pytest.mark.version("master")
def test_quota(client: citric.Client, survey_id: int):
    """Test quota methods."""
    with pytest.raises(LimeSurveyStatusError, match="No quotas found"):
        client.list_quotas(survey_id)

    quota_id = client.add_quota(survey_id, "Test Quota", 100)

    # List quotas
    quotas = client.list_quotas(survey_id)
    assert len(quotas) == 1
    assert quotas[0]["id"] == quota_id

    # Get quota properties
    props = client.get_quota_properties(quota_id)
    assert props["id"] == quota_id
    assert props["name"] == "Test Quota"
    assert props["qlimit"] == 100
    assert props["active"] == 1
    assert props["action"] == enums.QuotaAction.TERMINATE.integer_value

    # Set quota properties
    response = client.set_quota_properties(quota_id, qlimit=150)
    assert response["success"] is True
    assert response["message"]["qlimit"] == 150

    # Delete quota
    delete_response = client.delete_quota(quota_id)
    assert delete_response["status"] == "OK"

    with pytest.raises(LimeSurveyStatusError, match="Error: Invalid quota ID"):
        client.get_quota_properties(quota_id)


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

    client.activate_tokens(survey_id, [1, 2, 3, 4, 5])

    with pytest.raises(LimeSurveyStatusError, match="No survey participants found"):
        client.list_participants(survey_id)


@pytest.mark.integration_test
def test_participants(faker: Faker, client: citric.Client, survey_id: int):
    """Test participants methods."""
    client.activate_survey(survey_id)
    client.activate_tokens(survey_id, [1, 2])

    data = [
        {
            "email": faker.email(),
            "firstname": faker.first_name(),
            "lastname": faker.last_name(),
            "token": "1",
            "attribute_1": "Dog person",
            "attribute_2": "Night owl",
        },
        {
            "email": faker.email(),
            "firstname": faker.first_name(),
            "lastname": faker.last_name(),
            "token": "2",
            "attribute_1": "Cat person",
            "attribute_2": "Early bird",
        },
        {
            "email": faker.email(),
            "firstname": faker.first_name(),
            "lastname": faker.last_name(),
            "token": "2",
            "attribute_1": "Cat person",
            "attribute_2": "Night owl",
        },
    ]

    # Add participants
    added = client.add_participants(
        survey_id,
        participant_data=data,
        create_tokens=False,
    )
    for p, d in zip(added, data):
        assert p["email"] == d["email"]
        assert p["firstname"] == d["firstname"]
        assert p["lastname"] == d["lastname"]
        assert p["attribute_1"] == d["attribute_1"]
        assert p["attribute_2"] == d["attribute_2"]

    participants = client.list_participants(
        survey_id,
        attributes=["attribute_1", "attribute_2"],
    )

    # Confirm that the participants are deduplicated based on token
    assert len(participants) == 2

    # Check added participant properties
    for p, d in zip(participants, data[:2]):
        assert p["participant_info"]["email"] == d["email"]
        assert p["participant_info"]["firstname"] == d["firstname"]
        assert p["participant_info"]["lastname"] == d["lastname"]
        assert p["attribute_1"] == d["attribute_1"]
        assert p["attribute_2"] == d["attribute_2"]

    # Get participant properties
    for p, d in zip(added, data[:2]):
        properties = client.get_participant_properties(survey_id, p["tid"])
        assert properties["email"] == d["email"]
        assert properties["firstname"] == d["firstname"]
        assert properties["lastname"] == d["lastname"]
        assert properties["attribute_1"] == d["attribute_1"]
        assert properties["attribute_2"] == d["attribute_2"]

    # Update participant properties
    new_firstname = faker.first_name()
    new_attribute_1 = "Hamster person"

    response = client.set_participant_properties(
        survey_id,
        added[0]["tid"],
        firstname=new_firstname,
        attribute_1=new_attribute_1,
    )
    assert response["firstname"] == new_firstname
    assert response["lastname"] == added[0]["lastname"]
    assert response["attribute_1"] == new_attribute_1

    # Delete participants
    deleted = client.delete_participants(survey_id, [added[0]["tid"]])
    assert deleted == {added[0]["tid"]: "Deleted"}
    assert len(client.list_participants(survey_id)) == 1


@pytest.mark.integration_test
def test_responses(client: citric.Client, survey_id: int):
    """Test adding and exporting responses."""
    client.activate_survey(survey_id)
    client.activate_tokens(survey_id)

    # Add a single response to a survey
    single_response = {"G01Q01": "Long text 1", "G01Q02": "1", "token": "T00000"}
    assert client.add_response(survey_id, single_response) == 1

    # Add multiple responses to a survey
    data: list[dict[str, Any]]
    data = [
        {"G01Q01": "Long text 2", "G01Q02": "5", "token": "T00001"},
        {"G01Q01": "Long text 3", "G01Q02": None, "token": "T00002"},
    ]
    assert client.add_responses(survey_id, data) == [2, 3]

    # Update a response
    client.set_survey_properties(survey_id, alloweditaftercompletion="Y")
    data[1]["G01Q01"] = "New long text 3"
    assert client.update_response(survey_id, data[1]) is True

    all_responses = [single_response, *data]

    with io.BytesIO() as file, io.TextIOWrapper(file, encoding="utf-8-sig") as textfile:
        file.write(client.export_responses(survey_id, file_format="csv"))
        file.seek(0)
        reader = csv.DictReader(textfile, delimiter=";")
        for i, row in enumerate(reader):
            assert row["G01Q01"] == (all_responses[i]["G01Q01"] or "")
            assert row["G01Q02"] == (all_responses[i]["G01Q02"] or "")
            assert row["token"] == (all_responses[i]["token"] or "")
        file.seek(0)

        file.write(
            client.export_responses(survey_id, token="T00002", file_format="csv"),
        )
        file.seek(0)
        reader = csv.DictReader(textfile, delimiter=";")
        row = next(reader)
        assert row["G01Q01"] == "New long text 3"
        assert not row["G01Q02"]
        assert row["token"] == "T00002"

    # Export existing response works
    client.export_responses(survey_id, token="T00000")

    # Delete a response and then fail to export it or update it
    client.delete_response(survey_id, 1)
    with pytest.raises(LimeSurveyStatusError, match="No Response found for Token"):
        client.export_responses(survey_id, token="T00000")

    with pytest.raises(LimeSurveyStatusError, match="No matching Response"):
        client.update_response(survey_id, all_responses[0])


@pytest.mark.integration_test
@pytest.mark.xfail_mysql
def test_file_upload(client: citric.Client, survey_id: int, tmp_path: Path):
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


@pytest.mark.integration_test
@pytest.mark.xfail_mysql
def test_file_upload_no_filename(client: citric.Client, survey_id: int, tmp_path: Path):
    """Test uploading and downloading files from a survey without a filename."""
    filepath = tmp_path / "hello world.txt"
    filepath.write_text("Hello world!")

    client.activate_survey(survey_id)
    group = client.list_groups(survey_id)[1]
    question = client.list_questions(survey_id, group["gid"])[0]

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


@pytest.mark.integration_test
@pytest.mark.xfail_mysql
def test_file_upload_invalid_extension(
    client: citric.Client,
    survey_id: int,
    tmp_path: Path,
):
    """Test uploading and downloading files from a survey with an invalid extension."""
    filepath = tmp_path / "hello world.abc"
    filepath.write_text("Hello world!")

    client.activate_survey(survey_id)
    group = client.list_groups(survey_id)[1]
    question = client.list_questions(survey_id, group["gid"])[0]

    with pytest.raises(
        LimeSurveyStatusError,
        match="The extension abc is not valid. Valid extensions are: txt",
    ):
        client.upload_file(
            survey_id,
            f"{survey_id}X{group['gid']}X{question['qid']}",
            filepath,
        )


@pytest.mark.integration_test
@pytest.mark.version("6-apache")
@pytest.mark.version("develop")
@pytest.mark.version("master")
def test_get_available_site_settings(client: citric.Client):
    """Test getting available site settings."""
    assert client.get_available_site_settings()


@pytest.mark.integration_test
def test_site_settings(client: citric.Client):
    """Test getting site settings."""
    assert client.get_available_languages() is None
    assert client.get_default_language() == "en"
    assert client.get_default_theme() == "fruity"
    assert client.get_site_name() == "Citric - Test"


@pytest.mark.integration_test
def test_cpdb(faker: Faker, client: citric.Client):
    """Test the CPDB methods."""
    participants = [
        Participant(
            email=faker.email(),
            firstname=faker.first_name(),
            lastname=faker.last_name(),
            participant_id=uuid.uuid4(),
            attributes={
                "favorite_color": "red",
            },
        ),
        Participant(
            email=faker.email(),
            firstname=faker.first_name(),
            lastname=faker.last_name(),
            participant_id=uuid.uuid4(),
        ),
    ]
    assert client.import_cpdb_participants(participants) == {
        "ImportCount": 2,
        "UpdateCount": 0,
    }

    more_participants = [
        Participant(
            email=participants[0].email,
            firstname=participants[0].firstname,
            lastname=participants[0].lastname,
            participant_id=participants[0].participant_id,
            attributes={
                "favorite_color": "blue",
            },
        ),
        Participant(
            email=faker.email(),
            firstname=faker.first_name(),
            lastname=faker.last_name(),
            participant_id=uuid.uuid4(),
        ),
    ]
    assert client.import_cpdb_participants(more_participants, update=True) == {
        "ImportCount": 1,
        "UpdateCount": 1,
    }

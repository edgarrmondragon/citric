"""Integration tests for Python client."""

from __future__ import annotations

import csv
import io
import json
import operator
import random
import typing as t
import uuid
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import pytest
import requests
import semver

import citric
from citric import enums
from citric.exceptions import LimeSurveyStatusError
from citric.objects import Participant

if t.TYPE_CHECKING:
    from faker import Faker
    from pytest_subtests import SubTests

    from tests.fixtures import MailHogClient

NEW_SURVEY_NAME = "New Survey"


@pytest.fixture
def participants(faker: Faker) -> list[dict[str, t.Any]]:
    """Create participants for a survey."""
    return [
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


@pytest.mark.integration_test
def test_fieldmap(client: citric.Client, survey_id: int, subtests: SubTests):
    """Test fieldmap."""
    fieldmap = client.get_fieldmap(survey_id)
    for key, value in fieldmap.items():
        with subtests.test(msg="test field", field=key):
            assert key == value["fieldname"]
            assert (
                key == "{sid}X{gid}X{qid}".format(**value)
                or not value["qid"]
                or "_" in key
            )


@pytest.mark.integration_test
def test_language(client: citric.Client, survey_id: int, subtests: SubTests):
    """Test language methods."""
    # Add a new language
    assert client.add_language(survey_id, "es")["status"] == "OK"
    assert client.add_language(survey_id, "ru")["status"] == "OK"

    survey_props = client.get_survey_properties(survey_id)
    with subtests.test(msg="additional languages are correct"):
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
    with subtests.test(msg="updated language properties"):
        assert response == {"status": "OK", "surveyls_email_confirm": True}

    new_props = client.get_language_properties(
        survey_id,
        language="es",
        settings=["surveyls_email_confirm"],
    )
    with subtests.test(msg="read updated language properties"):
        assert new_props["surveyls_email_confirm"] == new_confirmation

    # Delete language
    delete_response = client.delete_language(survey_id, "ru")
    assert delete_response["status"] == "OK"

    props_after_delete_language = client.get_survey_properties(survey_id)
    with subtests.test(msg="language is deleted"):
        assert props_after_delete_language["additional_languages"] == "es"


@pytest.mark.integration_test
def test_survey(client: citric.Client):
    """Test survey methods."""
    # Try to get a survey that doesn't exist
    with pytest.raises(LimeSurveyStatusError, match="Error: Invalid survey"):
        client.get_survey_properties(99999)

    # Try to delete a survey that doesn't exist
    with pytest.raises(LimeSurveyStatusError, match="No permission"):
        client.delete_survey(99999)

    # Add a new survey
    survey_id = client.add_survey(
        5555,
        NEW_SURVEY_NAME,
        "es",
        enums.NewSurveyType.GROUP_BY_GROUP,
    )

    # Copy a survey
    copied = client.copy_survey(survey_id, NEW_SURVEY_NAME)
    assert copied["status"] == "OK"

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
def test_import_survey(client: citric.Client, subtests: SubTests):
    """Test importing a survey with a custom ID and name."""
    survey_id = random.randint(10000, 20000)  # noqa: S311
    with Path("./examples/survey.lss").open("rb") as f:
        imported_id = client.import_survey(
            f,
            survey_id=survey_id,
            survey_name="Custom Name",
        )

    with subtests.test(msg="imported survey has custom ID"):
        assert imported_id == survey_id

    survey_props = client.get_language_properties(imported_id)
    with subtests.test(msg="imported survey has custom name"):
        assert survey_props["surveyls_title"] == "Custom Name"


@pytest.mark.integration_test
def test_copy_survey_destination_id(
    request: pytest.FixtureRequest,
    client: citric.Client,
    survey_id: int,
    server_version: semver.VersionInfo,
):
    """Test copying a survey with a destination survey ID."""
    request.applymarker(
        pytest.mark.xfail(
            server_version < semver.VersionInfo.parse("6.4.0-dev"),
            reason=(
                "The destination_survey_id parameter is not supported in LimeSurvey "
                f"{server_version} < 6.4.0"
            ),
            strict=True,
        ),
    )

    # Copy a survey, specifying a new survey ID
    copied = client.copy_survey(
        survey_id,
        NEW_SURVEY_NAME,
        destination_survey_id=9797,
    )

    assert copied["status"] == "OK"
    assert copied["newsid"] == 9797


@pytest.mark.integration_test
def test_group(client: citric.Client):
    """Test group methods."""
    # Create a new survey
    survey_id = client.add_survey(1234, "New Survey", "en")

    # Import a group
    with Path("./examples/group.lsg").open("rb") as f:
        imported_group = client.import_group(f, survey_id)

    # Create a new group
    created_group = client.add_group(
        survey_id,
        "Second Group",
        description="A new group",
    )

    # Get group properties
    group_props = client.get_group_properties(imported_group)
    assert int(group_props["gid"]) == imported_group
    assert int(group_props["sid"]) == survey_id
    assert group_props["group_name"] == "First Group"
    assert group_props["description"] == "<p>A new group</p>"
    assert int(group_props["group_order"]) == 1

    group_props = client.get_group_properties(created_group)
    assert int(group_props["gid"]) == created_group
    assert int(group_props["sid"]) == survey_id
    assert group_props["group_name"] == "Second Group"
    assert group_props["description"] == "A new group"
    assert int(group_props["group_order"]) == 2

    questions = sorted(
        client.list_questions(survey_id, imported_group),
        key=operator.itemgetter("qid"),
    )

    assert questions[0]["question"] == "<p><strong>First question</p>"
    assert questions[1]["question"] == "<p><strong>Second question</p>"

    # Update group properties
    response = client.set_group_properties(created_group, group_order=1)
    assert response == {"group_order": True}

    new_props = client.get_group_properties(created_group, settings=["group_order"])
    assert int(new_props["group_order"]) == 1

    with pytest.raises(LimeSurveyStatusError, match="Error: Invalid group ID"):
        client.set_group_properties(99999, group_order=1)

    # Delete group
    client.delete_group(survey_id, imported_group)
    with pytest.raises(LimeSurveyStatusError, match="Error: Invalid group ID"):
        client.get_group_properties(survey_id)


@pytest.mark.integration_test
def test_import_group_with_name(
    request: pytest.FixtureRequest,
    client: citric.Client,
    server_version: semver.VersionInfo,
    survey_id: int,
):
    """Test importing a group with a custom name."""
    request.applymarker(
        pytest.mark.xfail(
            server_version < semver.VersionInfo.parse("6.6.6"),
            reason=(
                f"The name override is broken in LimeSurvey {server_version} < 6.6.0"
            ),
            strict=True,
        ),
    )

    with Path("./examples/group.lsg").open("rb") as f:
        group_id = client.import_group(f, survey_id, name="Custom Name")

    group_props = client.get_group_properties(group_id)
    assert group_props["group_name"] == "Custom Name"


@pytest.mark.integration_test
def test_import_group_with_description(
    request: pytest.FixtureRequest,
    client: citric.Client,
    server_version: semver.VersionInfo,
    survey_id: int,
):
    """Test importing a group with a custom description."""
    request.applymarker(
        pytest.mark.xfail(
            server_version < semver.VersionInfo.parse("6.6.6"),
            reason=(
                "The description override is broken in LimeSurvey "
                f"{server_version} < 6.6.0"
            ),
            strict=True,
        ),
    )

    with Path("./examples/group.lsg").open("rb") as f:
        group_id = client.import_group(f, survey_id, description="Custom description")

    group_props = client.get_group_properties(group_id)
    assert group_props["description"] == "Custom description"


@pytest.mark.integration_test
def test_question(
    request: pytest.FixtureRequest,
    client: citric.Client,
    server_version: semver.VersionInfo,
    survey_id: int,
):
    """Test question methods."""
    request.applymarker(
        pytest.mark.xfail(
            server_version < (6, 6, 4),
            reason=(
                "The question text property (`question`) is not available in "
                f"LimeSurvey {server_version} < 6.6.4"
            ),
            raises=KeyError,
            strict=True,
        ),
    )

    group_id = client.add_group(survey_id, "Test Group")

    # Import a question from a lsq file
    with Path("./examples/free_text.lsq").open("rb") as f:
        question_id = client.import_question(f, survey_id, group_id)

    # Get question properties
    props = client.get_question_properties(question_id)

    # test language-specific question properties
    assert props["question"] == "<p>Text for <strong>first question</strong></p>"
    assert not props["help"]
    assert not props["script"]
    assert isinstance(props["questionl10ns"], dict)

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
def test_quota(
    request: pytest.FixtureRequest,
    client: citric.Client,
    server_version: semver.VersionInfo,
    survey_id: int,
):
    """Test quota methods."""
    request.applymarker(
        pytest.mark.xfail(
            server_version < (6, 0, 0),
            reason=(
                "Quota RPC methods are not supported in LimeSurvey "
                f"{server_version} < 6.0.0"
            ),
            raises=requests.exceptions.HTTPError,
            strict=True,
        ),
    )

    with pytest.raises(LimeSurveyStatusError, match="No quotas found"):
        client.list_quotas(survey_id)

    quota_id = client.add_quota(survey_id, "Test Quota", 100)

    # List quotas
    quotas = client.list_quotas(survey_id)
    assert len(quotas) == 1
    assert int(quotas[0]["id"]) == quota_id

    # Get quota properties
    props = client.get_quota_properties(quota_id)
    assert int(props["id"]) == quota_id
    assert props["name"] == "Test Quota"
    assert int(props["qlimit"]) == 100
    assert int(props["active"]) == 1
    assert int(props["action"]) == enums.QuotaAction.TERMINATE.integer_value

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
def test_activate_survey_with_settings(
    request: pytest.FixtureRequest,
    client: citric.Client,
    server_version: semver.VersionInfo,
    survey_id: int,
):
    """Test whether the survey gets activated with the requested settings."""
    min_version = (5, 6, 45) if server_version < (6, 0) else (6, 3, 5)
    request.applymarker(
        pytest.mark.xfail(
            server_version < min_version,
            reason=(
                "The user_activation_settings parameter is not supported in LimeSurvey "
                f"{server_version} < {'.'.join(str(v) for v in min_version)}"
            ),
            strict=True,
        ),
    )

    properties_before = client.get_survey_properties(
        survey_id,
        ["active", "anonymized", "ipaddr"],
    )
    assert properties_before["active"] == "N"
    assert properties_before["anonymized"] == "N"
    assert properties_before["ipaddr"] == "I"

    result = client.activate_survey(
        survey_id,
        user_activation_settings={
            "anonymized": True,
            "ipaddr": False,
        },
    )
    assert result["status"] == "OK"

    properties_after = client.get_survey_properties(
        survey_id,
        ["active", "anonymized", "ipaddr"],
    )
    assert properties_after["active"] == "Y"
    assert properties_after["anonymized"] == "Y"
    assert properties_after["ipaddr"] == "N"


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
def test_participants(
    faker: Faker,
    client: citric.Client,
    survey_id: int,
    participants: list[dict[str, str]],
    subtests: SubTests,
):
    """Test participants methods."""
    client.activate_survey(survey_id)
    client.activate_tokens(survey_id, [1, 2])

    # Add participants
    added = client.add_participants(
        survey_id,
        participant_data=participants,
        create_tokens=False,
    )
    for p, d in zip(added, participants):
        with subtests.test(msg="test new participants properties", token=d["token"]):
            assert p["email"] == d["email"]
            assert p["firstname"] == d["firstname"]
            assert p["lastname"] == d["lastname"]
            assert p["attribute_1"] == d["attribute_1"]
            assert p["attribute_2"] == d["attribute_2"]

    participants_list = client.list_participants(
        survey_id,
        attributes=["attribute_1", "attribute_2"],
    )

    # Confirm that the participants are deduplicated based on token
    assert len(participants_list) == 2

    # Check added participant properties
    for p, d in zip(participants_list, participants[:2]):
        with subtests.test(msg="test new participants properties", token=p["tid"]):
            assert p["participant_info"]["email"] == d["email"]
            assert p["participant_info"]["firstname"] == d["firstname"]
            assert p["participant_info"]["lastname"] == d["lastname"]
            assert p["attribute_1"] == d["attribute_1"]
            assert p["attribute_2"] == d["attribute_2"]

    # Get participant properties
    for p, d in zip(added, participants[:2]):
        with subtests.test(msg="test updated participants properties", token=p["tid"]):
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
def test_invite_participants(
    client: citric.Client,
    survey_id: int,
    participants: list[dict[str, str]],
):
    """Test inviting participants to a survey."""
    client.activate_survey(survey_id)
    client.activate_tokens(survey_id, [1, 2])

    # Add participants
    client.add_participants(
        survey_id,
        participant_data=participants,
        create_tokens=False,
    )

    pending = enums.EmailSendStrategy.PENDING
    resend = enums.EmailSendStrategy.RESEND

    with pytest.raises(LimeSurveyStatusError, match="Error: No candidate tokens"):
        client.invite_participants(survey_id, strategy=resend)

    participant_data = client.list_participants(survey_id, attributes=["sent"])
    assert participant_data[0]["sent"] == "N"
    assert participant_data[1]["sent"] == "N"

    assert client.invite_participants(survey_id, strategy=pending) == 0

    participant_data = client.list_participants(survey_id, attributes=["sent"])
    date_format = "%Y-%m-%d %H:%M"
    datetime.strptime(participant_data[0]["sent"], date_format)  # noqa: DTZ007
    datetime.strptime(participant_data[1]["sent"], date_format)  # noqa: DTZ007

    with pytest.raises(LimeSurveyStatusError, match="Error: No candidate tokens"):
        client.invite_participants(survey_id, strategy=pending)

    assert client.invite_participants(survey_id, strategy=resend) == -2


@pytest.mark.integration_test
def test_responses(client: citric.Client, survey_id: int, tmp_path: Path):
    """Test adding and exporting responses."""
    client.activate_survey(survey_id)
    client.activate_tokens(survey_id)

    # Add a single response to a survey
    single_response = {"G01Q01": "Long text 1", "G01Q02": "1", "token": "T00000"}
    assert client.add_response(survey_id, single_response) == 1

    # Add multiple responses to a survey
    data: list[dict[str, t.Any]]
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

    # Save responses to a file
    filepath = tmp_path / "responses.json"
    client.save_responses(
        filepath,
        survey_id,
    )
    with filepath.open("r") as f:
        responses = json.load(f)

    assert len(responses["responses"]) == 3

    # Get response IDs for a token
    response_ids = client.get_response_ids(survey_id, token="T00000")
    assert response_ids == [1]

    # Delete a response and then fail to export it or update it
    client.delete_response(survey_id, 1)
    with pytest.raises(LimeSurveyStatusError, match="No Response found for Token"):
        client.export_responses(survey_id, token="T00000")

    with pytest.raises(LimeSurveyStatusError, match="No matching Response"):
        client.update_response(survey_id, all_responses[0])


@pytest.mark.integration_test
def test_file_upload(
    client: citric.Client,
    survey_id: int,
    tmp_path: Path,
    faker: Faker,
):
    """Test uploading and downloading files from a survey."""
    filepath = tmp_path / "hello world.txt"
    filepath.write_text(faker.text())

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
    assert result["size"] == pytest.approx(filepath.stat().st_size / 1000, rel=1e-2)
    assert result["name"] == filename
    assert result["ext"] == "txt"
    assert "filename" in result
    assert "msg" in result


@pytest.mark.integration_test
@pytest.mark.xfail_mysql
def test_file_upload_no_filename(
    client: citric.Client,
    survey_id: int,
    tmp_path: Path,
    faker: Faker,
):
    """Test uploading and downloading files from a survey without a filename."""
    filepath = tmp_path / "hello world.txt"
    filepath.write_text(faker.text())

    client.activate_survey(survey_id)
    group = client.list_groups(survey_id)[1]
    question = client.list_questions(survey_id, group["gid"])[0]

    result_no_filename = client.upload_file(
        survey_id,
        f"{survey_id}X{group['gid']}X{question['qid']}",
        filepath,
    )
    assert result_no_filename["success"]
    assert result_no_filename["size"] == pytest.approx(
        filepath.stat().st_size / 1000,
        rel=1e-2,
    )
    assert result_no_filename["name"] == quote(filepath.name)
    assert result_no_filename["ext"] == "txt"
    assert "filename" in result_no_filename
    assert "msg" in result_no_filename


@pytest.mark.integration_test
def test_file_upload_invalid_extension(
    client: citric.Client,
    survey_id: int,
    tmp_path: Path,
    faker: Faker,
):
    """Test uploading and downloading files from a survey with an invalid extension."""
    filepath = tmp_path / "hello world.abc"
    filepath.write_text(faker.text())

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
def test_get_available_site_settings(
    request: pytest.FixtureRequest,
    client: citric.Client,
    server_version: semver.VersionInfo,
):
    """Test getting available site settings."""
    request.applymarker(
        pytest.mark.xfail(
            server_version < (6, 0, 0),
            reason=(
                "RPC method `get_available_site_settings` is not supported in "
                f"LimeSurvey {server_version} < 6.0.0"
            ),
            raises=requests.exceptions.HTTPError,
            strict=True,
        ),
    )
    assert client.get_available_site_settings()


@pytest.mark.integration_test
def test_site_settings(client: citric.Client):
    """Test getting site settings."""
    assert client.get_available_languages() is None
    assert client.get_default_language() == "en"
    assert client.get_default_theme() == "vanilla"
    assert client.get_site_name() == "Citric - Test"


@pytest.mark.integration_test
def test_missing_setting(client: citric.Client):
    """Test getting site settings."""
    with pytest.raises(LimeSurveyStatusError, match="Invalid setting"):
        client._get_site_setting("not_a_valid_setting")


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


@pytest.mark.integration_test
def test_users(client: citric.Client):
    """Test user methods."""
    assert len(client.list_users()) == 1


@pytest.mark.integration_test
def test_survey_groups(client: citric.Client):
    """Test survey group methods."""
    assert len(client.list_survey_groups()) == 1


@pytest.mark.integration_test
def test_mail_registered_participants(
    client: citric.Client,
    survey_id: int,
    participants: list[dict[str, str]],
    mailhog: MailHogClient,
    subtests: SubTests,
):
    """Test mail_registered_participants."""
    client.activate_survey(survey_id)
    client.activate_tokens(survey_id, [1, 2])
    client.add_participants(
        survey_id,
        participant_data=participants,
        create_tokens=False,
    )

    with subtests.test(msg="No initial emails"):
        assert mailhog.get_all()["total"] == 0

    # `mail_registered_participants` returns a non-error status messages even when
    # emails are sent successfully and that violates assumptions made by this
    # library about the meaning of `status` messages
    with pytest.raises(
        LimeSurveyStatusError,
        match="0 left to send",
    ):
        client.session.mail_registered_participants(survey_id)

    with subtests.test(msg="2 emails sent"):
        assert mailhog.get_all()["total"] == 2

    mailhog.delete()

    with pytest.raises(
        LimeSurveyStatusError,
        match="Error: No candidate tokens",
    ):
        client.session.mail_registered_participants(survey_id)

    with subtests.test(msg="No more emails sent"):
        assert mailhog.get_all()["total"] == 0


@pytest.mark.integration_test
def test_remind_participants(
    client: citric.Client,
    survey_id: int,
    participants: list[dict[str, str]],
    mailhog: MailHogClient,
    subtests: SubTests,
):
    """Test remind_participants."""
    client.activate_survey(survey_id)
    client.activate_tokens(survey_id, [1, 2])
    client.add_participants(
        survey_id,
        participant_data=participants,
        create_tokens=False,
    )

    with subtests.test(msg="No initial emails"):
        assert mailhog.get_all()["total"] == 0

    # Use `call` to avoid error handling
    client.session.call("mail_registered_participants", survey_id)

    with subtests.test(msg="2 emails sent"):
        assert mailhog.get_all()["total"] == 2

    mailhog.delete()

    # `remind_participants` returns a non-error status messages even when emails are
    # sent successfully and that violates assumptions made by this library about the
    # meaning of `status` messages"
    with pytest.raises(LimeSurveyStatusError, match="0 left to send"):
        client.session.remind_participants(survey_id)

    with subtests.test(msg="2 reminders sent"):
        assert mailhog.get_all()["total"] == 2

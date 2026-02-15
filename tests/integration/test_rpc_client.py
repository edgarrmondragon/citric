"""Integration tests for Python client."""

from __future__ import annotations

import csv
import io
import json
import operator
import random
import uuid
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import quote

import bs4
import pytest
import requests.exceptions
import semver

import citric
from citric import enums
from citric.exceptions import LimeSurveyApiError, LimeSurveyStatusError
from citric.objects import Participant

if TYPE_CHECKING:
    from faker import Faker

    from citric.types import QuestionsListElement
    from tests.fixtures import MailpitClient

NEW_SURVEY_NAME = "New Survey"


@pytest.fixture
def participants(faker: Faker) -> list[dict[str, Any]]:
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
def test_fieldmap(client: citric.Client, survey_id: int, subtests: pytest.Subtests):
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
def test_language(client: citric.Client, survey_id: int, subtests: pytest.Subtests):
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
def test_survey(
    client: citric.Client,
    server_version: semver.VersionInfo,
    subtests: pytest.Subtests,
):
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

    with subtests.test(msg="survey group ID"):
        if server_version < (6, 10, 0):
            pytest.xfail(
                "The gsid field is not available as input nor output of the RPC "
                "list_surveys method in LimeSurvey < 6.10.0"
            )

        gsid = matched["gsid"]
        surveys_in_group = client.list_surveys(survey_group_id=gsid)
        assert all(s["gsid"] == gsid for s in surveys_in_group)

    # Update survey properties
    response = client.set_survey_properties(
        survey_id,
        format=enums.NewSurveyType.ALL_ON_ONE_PAGE,
    )
    assert response == {"format": True}

    new_props = client.get_survey_properties(survey_id, properties=["format"])
    assert new_props["format"] == enums.NewSurveyType.ALL_ON_ONE_PAGE


@pytest.mark.integration_test
def test_import_survey(client: citric.Client, subtests: pytest.Subtests):
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

    assert any(q["question"] == "<p><strong>First question</p>" for q in questions)
    assert any(q["question"] == "<p><strong>Second question</p>" for q in questions)

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
            server_version < (6, 6, 7),
            reason=(
                f"The name override is broken in LimeSurvey {server_version} < 6.6.7"
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
            server_version < (6, 6, 7),
            reason=(
                "The description override is broken in LimeSurvey "
                f"{server_version} < 6.6.7"
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
    assert props["mandatory"] == "N"

    # Update question properties
    response = client.set_question_properties(question_id, mandatory="Y")
    assert response == {"mandatory": True}

    new_props = client.get_question_properties(question_id, settings=["mandatory"])
    assert new_props["mandatory"] == "Y"

    # Delete question
    client.delete_question(question_id)

    with pytest.raises(LimeSurveyStatusError, match="No questions found"):
        client.list_questions(survey_id, group_id)

    # Import a question from a lsq file and apply some overrides
    with Path("./examples/free_text.lsq").open("rb") as f:
        new_title = f"NEW{uuid.uuid4().hex[:6].upper()}"
        new_text = f"New Text: {uuid.uuid4()}"
        new_help = f"New Help: {uuid.uuid4()}"
        question_id = client.import_question(
            f,
            survey_id,
            group_id,
            mandatory=True,
            new_question_title=new_title,
            new_question_text=new_text,
            new_question_help=new_help,
        )

    props = client.get_question_properties(question_id)
    assert props["question"] == new_text
    assert props["help"] == new_help
    assert props["title"] == new_title
    assert props["mandatory"] == "Y"


@pytest.mark.integration_test
def test_quota(
    request: pytest.FixtureRequest,
    client: citric.Client,
    server_version: semver.VersionInfo,
    survey_id: int,
    subtests: pytest.Subtests,
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

    quota_id = client.add_quota(
        survey_id,
        "Test Quota",
        100,
        message="No more responses allowed",
        url="https://example.com",
        url_description="Learn more",
    )

    # List quotas
    quotas = client.list_quotas(survey_id)
    assert len(quotas) == 1
    assert int(quotas[0]["id"]) == quota_id

    # Get quota properties
    client.activate_survey(survey_id)
    props = client.get_quota_properties(quota_id)
    assert int(props["id"]) == quota_id
    assert props["name"] == "Test Quota"
    assert int(props["qlimit"]) == 100
    assert int(props["active"]) == 1
    assert int(props["action"]) == enums.QuotaAction.TERMINATE.integer_value

    # Language-specific quota properties
    with subtests.test(msg="language-specific quota properties"):
        assert props["quotals_message"] == "No more responses allowed"
        assert props["quotals_url"] == "https://example.com"
        assert props["quotals_urldescrip"] == "Learn more"

    with subtests.test(msg="completeCount"):
        if server_version < (6, 9, 0):
            pytest.xfail("completeCount is not supported in LimeSurvey < 6.9.0")
        props = client.get_quota_properties(quota_id)
        assert int(props["completeCount"]) == 0

    # Set quota properties
    response = client.set_quota_properties(quota_id, qlimit=150)
    assert response["success"] is True
    assert response["message"]["qlimit"] == 150

    # Delete quota
    delete_response = client.delete_quota(quota_id)
    assert delete_response["status"] == "OK"

    with pytest.raises(LimeSurveyStatusError, match="Error: Invalid quota ID"):
        client.get_quota_properties(quota_id)


@pytest.mark.parametrize(
    ("action", "min_version"),
    [
        pytest.param(
            enums.QuotaAction.TERMINATE,
            "6.0.0",
            id=enums.QuotaAction.TERMINATE,
        ),
        pytest.param(
            enums.QuotaAction.CONFIRM_TERMINATE,
            "6.0.0",
            id=enums.QuotaAction.CONFIRM_TERMINATE,
        ),
        # New (6.6.7+) quota options
        pytest.param(
            enums.QuotaAction.TERMINATE_PAGES,
            "6.6.7",
            id=enums.QuotaAction.TERMINATE_PAGES,
        ),
        pytest.param(
            enums.QuotaAction.TERMINATE_VISIBLE_HIDDEN,
            "6.6.7",
            id=enums.QuotaAction.TERMINATE_VISIBLE_HIDDEN,
        ),
    ],
)
@pytest.mark.integration_test
def test_add_quota(
    request: pytest.FixtureRequest,
    client: citric.Client,
    server_version: semver.VersionInfo,
    survey_id: int,
    action: enums.QuotaAction,
    min_version: str,
):
    """Test adding a quota."""
    request.applymarker(
        pytest.mark.xfail(
            server_version < semver.VersionInfo.parse(min_version),
            reason=(
                "Operation is not supported in LimeSurvey "
                f"{server_version} < {min_version}"
            ),
            strict=True,
        ),
    )
    quota_id = client.add_quota(survey_id, "Test Quota", 100, action=action)
    props = client.get_quota_properties(quota_id)
    assert int(props["action"]) == action.integer_value


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
def test_activate_tokens(
    client: citric.Client,
    survey_id: int,
    server_version: semver.VersionInfo,
):
    """Test whether the participants table gets activated."""
    client.activate_survey(survey_id)

    # LimeSurvey 6.15.4+ changed the error message
    if server_version >= (6, 15, 4):
        expected_pattern = "Error: No survey participant list"
    else:
        expected_pattern = "No survey participants table"

    with pytest.raises(LimeSurveyStatusError, match=expected_pattern):
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
    subtests: pytest.Subtests,
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
    for p, d in zip(added, participants, strict=False):
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
    for ple, d in zip(participants_list, participants[:2], strict=False):
        with subtests.test(msg="test new participants properties", token=ple["tid"]):
            assert ple["participant_info"]["email"] == d["email"]
            assert ple["participant_info"]["firstname"] == d["firstname"]
            assert ple["participant_info"]["lastname"] == d["lastname"]
            assert ple["attribute_1"] == d["attribute_1"]  # type: ignore[typeddict-item]
            assert ple["attribute_2"] == d["attribute_2"]  # type: ignore[typeddict-item]

    # Get participant properties
    for p, d in zip(added, participants[:2], strict=False):
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


@pytest.fixture
def responses() -> list[dict]:
    """Create responses for a survey."""
    return [
        {
            "G01Q01": "Long text 1",
            "G01Q02": "1",
            "G02Q04": "Y",
            "token": "T00000",
        },
        {
            "G01Q01": "Long text 2",
            "G01Q02": "5",
            "G02Q04": "N",
            "token": "T00001",
        },
        {
            "G01Q01": "Long text 3",
            "G01Q02": None,
            "G02Q04": "Y",
            "token": "T00002",
        },
    ]


@pytest.mark.integration_test
def test_responses(
    client: citric.Client,
    server_version: semver.VersionInfo,
    survey_id: int,
    responses: list[dict],
    tmp_path: Path,
    subtests: pytest.Subtests,
):
    """Test adding and exporting responses."""
    client.activate_survey(survey_id)
    client.activate_tokens(survey_id)

    # Add a single response to a survey
    assert client.add_response(survey_id, responses[0]) == 1

    # Add multiple responses to a survey
    assert client.add_responses(survey_id, responses[1:]) == [2, 3]

    # Update a response
    client.set_survey_properties(survey_id, alloweditaftercompletion="Y")
    responses[2]["G01Q01"] = "New long text 3"
    assert client.update_response(survey_id, responses[2]) is True

    with io.BytesIO() as file, io.TextIOWrapper(file, encoding="utf-8-sig") as textfile:
        file.write(client.export_responses(survey_id, file_format="csv"))
        file.seek(0)
        reader = csv.DictReader(textfile, delimiter=";")
        for i, row in enumerate(reader):
            assert row["G01Q01"] == (responses[i]["G01Q01"] or "")
            assert row["G01Q02"] == (responses[i]["G01Q02"] or "")
            assert row["G02Q04"] == responses[i]["G02Q04"]
            assert row["token"] == (responses[i]["token"] or "")
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

    with subtests.test(msg="Convert Y to 'true' and N to 'false'"):
        json_responses = client.export_responses(
            survey_id,
            file_format="json",
            additional_options={
                "convertY": True,
                "yValue": "true",
                "convertN": True,
                "nValue": "false",
            },
        )
        json_data = json.loads(json_responses)
        for i, response in enumerate(json_data["responses"]):
            bool_string_value = "true" if responses[i]["G02Q04"] == "Y" else "false"
            assert response["G02Q04"] == bool_string_value

    with subtests.test(msg="Convert Y to 1 and N to 0"):
        if server_version < (6, 11, 0):
            pytest.xfail(
                f"LimeSurvey {server_version} < 6.11.0 doesn't support 0 for "
                "answer codes"
            )

        json_responses = client.export_responses(
            survey_id,
            file_format="json",
            additional_options={
                "convertY": True,
                "yValue": 1,
                "convertN": True,
                "nValue": 0,
            },
        )
        json_data = json.loads(json_responses)
        for i, response in enumerate(json_data["responses"]):
            int_value = 1 if responses[i]["G02Q04"] == "Y" else 0
            assert response["G02Q04"] == int_value

    # Save responses to a file
    filepath = tmp_path / "responses.json"
    client.save_responses(
        filepath,
        survey_id,
    )
    with filepath.open("r") as f:
        file_responses = json.load(f)

    assert len(file_responses["responses"]) == 3

    # Get response IDs for a token
    response_ids = client.get_response_ids(survey_id, token="T00000")
    assert response_ids == [1]

    # Delete a response and then fail to export it or update it
    client.delete_response(survey_id, 1)

    with pytest.raises(LimeSurveyStatusError, match="No Response found for Token"):
        client.export_responses(survey_id, token="T00000")

    with pytest.raises(LimeSurveyStatusError, match="No matching Response"):
        client.update_response(survey_id, responses[0])


@pytest.mark.integration_test
def test_summary(
    client: citric.Client,
    survey_id: int,
    participants: list[dict],
    responses: list[dict],
    subtests: pytest.Subtests,
):
    """Test get_summary client method."""
    with (
        subtests.test(msg="Use get_summary"),
        pytest.raises(ValueError, match="Use get_summary"),
    ):
        client.get_summary_stat(survey_id, "all")  # type: ignore[arg-type]

    with (
        subtests.test(msg="Invalid stat name"),
        pytest.raises(LimeSurveyStatusError, match="Invalid summary key"),
    ):
        client.get_summary_stat(survey_id, "not_valid")  # type: ignore[arg-type]

    with subtests.test(msg="Without a participants table"):
        assert client.get_summary(survey_id) is None

        with pytest.raises(LimeSurveyStatusError, match="No available data"):
            client.get_summary_stat(survey_id, "token_count")

    with subtests.test(msg="Without responses"):
        client.activate_tokens(survey_id, [1, 2])
        client.add_participants(
            survey_id,
            participant_data=participants,
            create_tokens=False,
        )
        summary = client.get_summary(survey_id)
        assert summary is not None
        assert int(summary["token_count"]) == 2
        assert "completed_responses" not in summary
        assert client.get_summary_stat(survey_id, "token_count") == 2

        with pytest.raises(LimeSurveyStatusError, match="No available data"):
            client.get_summary_stat(survey_id, "completed_responses")

    with subtests.test(msg="With responses"):
        client.activate_survey(survey_id)
        client.add_responses(survey_id, responses)
        summary = client.get_summary(survey_id)
        assert summary is not None
        assert int(summary["completed_responses"]) == 3
        assert int(summary["incomplete_responses"]) == 0
        assert client.get_summary_stat(survey_id, "completed_responses") == 3


@pytest.fixture
def file_upload_question(
    client: citric.Client,
    survey_id: int,
) -> QuestionsListElement:
    """Create a file upload question."""
    client.activate_survey(survey_id)
    groups = client.list_groups(survey_id)
    group = next(filter(lambda g: g["group_name"] == "Second Group", groups), None)
    assert group is not None

    questions = client.list_questions(survey_id, group["gid"])
    question = next(
        filter(lambda q: q["title"] == "G02Q03", questions),
        None,
    )
    assert question is not None

    return question


@pytest.mark.integration_test
def test_response_files(
    client: citric.Client,
    survey_id: int,
    file_upload_question: QuestionsListElement,
    tmp_path: Path,
    faker: Faker,
):
    """Test response files."""
    token = "T00000"
    sid = file_upload_question["sid"]
    gid = file_upload_question["gid"]
    qid = file_upload_question["qid"]
    field_name = f"{sid}X{gid}X{qid}"

    # Upload two files
    with io.BytesIO() as file:
        content1 = faker.zip()
        file.write(content1)
        file.seek(0)
        result1 = client.upload_file_object(survey_id, field_name, "file1.zip", file)

    with io.BytesIO() as file:
        content2 = faker.zip()
        file.write(content2)
        file.seek(0)
        result2 = client.upload_file_object(survey_id, field_name, "file2.zip", file)

    # Add a response
    response_files = [result1, result2]
    responses = [
        {
            "token": token,
            field_name: json.dumps(response_files),
            f"{field_name}_filecount": len(response_files),
        },
    ]
    assert client.add_responses(survey_id, responses) == [1]

    export = json.loads(client.export_responses(survey_id, token=token))
    assert len(export["responses"]) == 1
    assert len(json.loads(export["responses"][0]["G02Q03"])) == 2
    assert int(export["responses"][0]["G02Q03[filecount]"]) == 2

    # Get uploaded files
    files = list(client.get_uploaded_file_objects(survey_id, token))
    assert len(files) == 2

    assert files[0]["meta"]["filename"] == result1["filename"]
    assert files[0]["meta"]["size"] == result1["size"]
    assert files[0]["meta"]["ext"] == result1["ext"]
    assert files[0]["meta"]["name"] == result1["name"]
    assert files[0]["content"].read() == content1

    assert files[1]["meta"]["filename"] == result2["filename"]
    assert files[1]["meta"]["size"] == result2["size"]
    assert files[1]["meta"]["ext"] == result2["ext"]
    assert files[1]["meta"]["name"] == result2["name"]
    assert files[1]["content"].read() == content2

    # Download files to a directory
    download_dir = tmp_path / "downloads"
    download_dir.mkdir(parents=True, exist_ok=True)
    paths = client.download_files(download_dir, survey_id, token)
    assert len(paths) == 2
    assert paths[0].read_bytes() == content1
    assert paths[1].read_bytes() == content2


@pytest.mark.integration_test
def test_file_upload(
    client: citric.Client,
    file_upload_question: QuestionsListElement,
    tmp_path: Path,
    faker: Faker,
):
    """Test uploading and downloading files from a survey."""
    filepath = tmp_path / "file.zip"
    filepath.write_bytes(faker.zip())

    sid = file_upload_question["sid"]
    gid = file_upload_question["gid"]
    qid = file_upload_question["qid"]

    filename = "upload.zip"
    result = client.upload_file(sid, f"{sid}X{gid}X{qid}", filepath, filename=filename)
    assert result["success"]
    assert result["size"] == pytest.approx(filepath.stat().st_size / 1000, rel=5e-2)
    assert result["name"] == filename
    assert result["ext"] == "zip"
    assert "filename" in result
    assert "msg" in result


@pytest.mark.integration_test
def test_file_upload_no_filename(
    client: citric.Client,
    file_upload_question: QuestionsListElement,
    tmp_path: Path,
    faker: Faker,
):
    """Test uploading and downloading files from a survey without a filename."""
    filepath = tmp_path / "file.zip"
    filepath.write_bytes(faker.zip())

    sid = file_upload_question["sid"]
    gid = file_upload_question["gid"]
    qid = file_upload_question["qid"]

    result_no_filename = client.upload_file(sid, f"{sid}X{gid}X{qid}", filepath)
    assert result_no_filename["success"]
    assert result_no_filename["size"] == pytest.approx(
        filepath.stat().st_size / 1000,
        rel=5e-2,
    )
    assert result_no_filename["name"] == quote(filepath.name)
    assert result_no_filename["ext"] == "zip"
    assert "filename" in result_no_filename
    assert "msg" in result_no_filename


@pytest.mark.integration_test
def test_file_upload_invalid_extension(
    client: citric.Client,
    file_upload_question: QuestionsListElement,
    tmp_path: Path,
    faker: Faker,
):
    """Test uploading and downloading files from a survey with an invalid extension."""
    filepath = tmp_path / "file.abc"
    filepath.write_bytes(faker.zip())

    sid = file_upload_question["sid"]
    gid = file_upload_question["gid"]
    qid = file_upload_question["qid"]

    with pytest.raises(
        LimeSurveyStatusError,
        match="The extension abc is not valid\\. Valid extensions are: zip",
    ):
        client.upload_file(sid, f"{sid}X{gid}X{qid}", filepath)


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
    assert client.get_default_theme() == "fruity_twentythree"
    assert client.get_site_name() == "Citric - Test"
    assert isinstance(client.get_db_version(), int)


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
def test_users(client: citric.Client, integration_username: str):
    """Test user methods."""
    all_users = client.list_users()
    assert len(all_users) == 1

    user_username = client.list_users(username=integration_username)
    assert len(user_username) == 1
    assert int(user_username[0]["uid"]) == 1

    user_id = client.list_users(user_id=1)
    assert len(user_id) == 1
    assert int(user_id[0]["uid"]) == 1

    with pytest.raises(LimeSurveyStatusError, match="Invalid username"):
        client.list_users(username="not_a_valid_username")

    with pytest.raises(LimeSurveyStatusError, match=r"Invalid user (ID|id)"):
        client.list_users(user_id=999999999)


@pytest.mark.integration_test
def test_survey_groups(client: citric.Client):
    """Test survey group methods."""
    assert len(client.list_survey_groups()) == 1


@pytest.mark.integration_test
def test_mail_registered_participants(
    client: citric.Client,
    survey_id: int,
    participants: list[dict[str, str]],
    mailpit: MailpitClient,
    subtests: pytest.Subtests,
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
        assert mailpit.get_all()["total"] == 0

    # `mail_registered_participants` returns a non-error status messages even when
    # emails are sent successfully and that violates assumptions made by this
    # library about the meaning of `status` messages
    with pytest.raises(
        LimeSurveyStatusError,
        match="0 left to send",
    ):
        client.session.mail_registered_participants(survey_id)

    with subtests.test(msg="2 emails sent"):
        assert mailpit.get_all()["total"] == 2

    mailpit.delete()

    with pytest.raises(
        LimeSurveyStatusError,
        match="Error: No candidate tokens",
    ):
        client.session.mail_registered_participants(survey_id)

    with subtests.test(msg="No more emails sent"):
        assert mailpit.get_all()["total"] == 0


@pytest.mark.integration_test
def test_remind_participants(
    client: citric.Client,
    survey_id: int,
    participants: list[dict[str, str]],
    mailpit: MailpitClient,
    subtests: pytest.Subtests,
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
        assert mailpit.get_all()["total"] == 0

    # Use `call` to avoid error handling
    client.session.call("mail_registered_participants", survey_id)

    with subtests.test(msg="2 emails sent"):
        assert mailpit.get_all()["total"] == 2

    mailpit.delete()

    # `remind_participants` returns a non-error status messages even when emails are
    # sent successfully and that violates assumptions made by this library about the
    # meaning of `status` messages"
    with pytest.raises(LimeSurveyStatusError, match="0 left to send"):
        client.session.remind_participants(survey_id)

    with subtests.test(msg="2 reminders sent"):
        assert mailpit.get_all()["total"] == 2


@pytest.mark.integration_test
def test_save_statistics(client: citric.Client, survey_id: int, tmp_path: Path):
    """Test save_statistics."""
    file_path = tmp_path / "statistics.csv"

    with pytest.raises(
        LimeSurveyApiError,
        match="cannot be found in the database",
    ):
        client.save_statistics(file_path, survey_id)

    client.activate_survey(survey_id)
    assert (
        client.save_statistics(
            file_path,
            survey_id,
            file_format=enums.StatisticsExportFormat.HTML,
        )
        > 0
    )
    # Check that the contents are valid HTML
    content = file_path.read_bytes()
    soup = bs4.BeautifulSoup(content, "html.parser")

    # Find the table elements
    tables = soup.find_all("table")
    assert len(tables) == 4  # One for each question

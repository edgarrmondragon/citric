# pyright: reportTypedDictNotRequiredAccess=none

"""Integration tests for the REST client."""

from __future__ import annotations

import contextlib
import operator
from typing import TYPE_CHECKING, Any

import pytest

from citric.exceptions import LimeSurveyStatusError
from citric.rest import RESTClient

if TYPE_CHECKING:
    from collections.abc import Generator

    from citric import Client


@pytest.fixture(scope="module")
def rest_client(
    client: Client,
    integration_url: str,
    integration_username: str,
    integration_password: str,
) -> Generator[RESTClient, None, None]:
    """LimeSurvey REST API client."""
    with RESTClient(
        integration_url,
        integration_username,
        integration_password,
    ) as api_client:
        yield api_client

    with contextlib.suppress(LimeSurveyStatusError):
        for survey in client.list_surveys(integration_username):
            client.delete_survey(survey["sid"])


@pytest.mark.integration_test
def test_refresh_token(rest_client: RESTClient) -> None:
    """Test refreshing the token."""
    session_id = rest_client.session_id
    rest_client.refresh_token()
    assert session_id != rest_client.session_id


@pytest.mark.integration_test
def test_get_surveys(rest_client: RESTClient, survey_id: int) -> None:
    """Test getting surveys."""
    surveys = rest_client.get_surveys()
    assert len(surveys) > 0

    survey = next(filter(lambda s: s["sid"] == survey_id, surveys), None)
    assert survey is not None


@pytest.mark.integration_test
def test_get_survey_details(rest_client: RESTClient, survey_id: int) -> None:
    """Test getting surveys."""
    survey = rest_client.get_survey_details(survey_id=survey_id)
    assert survey["sid"] == survey_id


@pytest.mark.integration_test
def test_patch_survey_details(rest_client: RESTClient, survey_id: int) -> None:
    """Test getting surveys."""
    original = rest_client.get_survey_details(survey_id=survey_id)
    anonymized = original["anonymized"]
    token_length = original["tokenLength"]

    result = rest_client.update_survey_details(
        survey_id=survey_id,
        anonymized=not anonymized,
        tokenLength=token_length + 10,
    )
    expected = {
        "operationsApplied": 1,
    }
    assert result == expected

    updated = rest_client.get_survey_details(survey_id=survey_id)
    assert updated["anonymized"] is (not anonymized)
    assert updated["tokenLength"] == token_length + 10


@pytest.mark.integration_test
def test_update_question_answers(
    rest_client: RESTClient,
    survey_with_question_answers: int,
) -> None:
    """Test updating question answers."""

    def _question_answers(s: dict[str, Any]) -> tuple[int, list]:
        question = next(
            q for q in s["questionGroups"][0]["questions"] if q.get("answers")
        )
        return question["qid"], question["answers"]

    survey = rest_client.get_survey_details(survey_id=survey_with_question_answers)
    qid, answers = _question_answers(survey)
    sorted_answers = sorted(answers, key=operator.itemgetter("sortOrder"))
    assert len(sorted_answers) == 5
    assert sorted_answers[0]["l10ns"]["en"]["answer"] == "Too much"
    assert sorted_answers[2]["l10ns"]["en"]["answer"] == "Just Right"
    assert sorted_answers[4]["l10ns"]["en"]["answer"] == "Too little"

    # Update text of answers
    sorted_answers[0]["l10ns"]["en"]["answer"] = "TOO MUCH!"
    sorted_answers[2]["l10ns"]["en"]["answer"] = "JAR"
    sorted_answers[4]["l10ns"]["en"]["answer"] = "TOO LITTLE!"

    operations = rest_client.patch_survey(
        survey_id=survey_with_question_answers,
        patch_operations=[
            {
                "entity": "answer",
                "op": "update",
                "id": qid,
                "props": [
                    # This removes the other answers
                    sorted_answers[0],
                    sorted_answers[2],
                    sorted_answers[4],
                ],
            },
        ],
    )
    assert operations["operationsApplied"] == 1

    survey = rest_client.get_survey_details(survey_id=survey_with_question_answers)
    qid, question_answers = _question_answers(survey)
    sorted_answers = sorted(question_answers, key=operator.itemgetter("sortOrder"))
    assert len(sorted_answers) == 3
    assert sorted_answers[0]["l10ns"]["en"]["answer"] == "TOO MUCH!"
    assert sorted_answers[1]["l10ns"]["en"]["answer"] == "JAR"
    assert sorted_answers[2]["l10ns"]["en"]["answer"] == "TOO LITTLE!"


@pytest.mark.integration_test
def test_patch_question(
    rest_client: RESTClient,
    survey_with_question_answers: int,
) -> None:
    """Test patching a question's properties."""
    survey = rest_client.get_survey_details(survey_id=survey_with_question_answers)
    question = survey["questionGroups"][0]["questions"][0]
    qid = question["qid"]

    result = rest_client.patch_survey(
        survey_id=survey_with_question_answers,
        patch_operations=[
            {
                "entity": "question",
                "op": "update",
                "id": qid,
                "props": {"mandatory": True},
            },
        ],
    )
    assert result["operationsApplied"] == 1

    updated_survey = rest_client.get_survey_details(
        survey_id=survey_with_question_answers
    )
    updated_question = next(
        q for q in updated_survey["questionGroups"][0]["questions"] if q["qid"] == qid
    )
    assert updated_question["mandatory"] is True


@pytest.mark.integration_test
def test_patch_question_l10n(
    rest_client: RESTClient,
    survey_with_question_answers: int,
) -> None:
    """Test patching question localizations."""
    survey = rest_client.get_survey_details(survey_id=survey_with_question_answers)
    question = survey["questionGroups"][0]["questions"][0]
    qid = question["qid"]
    new_text = "Updated question text"

    result = rest_client.patch_survey(
        survey_id=survey_with_question_answers,
        patch_operations=[
            {
                "entity": "questionL10n",
                "op": "update",
                "id": qid,
                "props": {"en": {"question": new_text}},
            },
        ],
    )
    assert result["operationsApplied"] == 1

    updated_survey = rest_client.get_survey_details(
        survey_id=survey_with_question_answers
    )
    updated_question = next(
        q for q in updated_survey["questionGroups"][0]["questions"] if q["qid"] == qid
    )
    assert updated_question["l10ns"]["en"]["question"] == new_text


@pytest.mark.integration_test
def test_patch_subquestions(
    rest_client: RESTClient,
    survey_with_question_answers: int,
) -> None:
    """Test patching subquestions."""

    def _subquestions(s: dict[str, Any]) -> tuple[int, list]:
        question = next(
            q for q in s["questionGroups"][0]["questions"] if q.get("subquestions")
        )
        return question["qid"], question["subquestions"]

    survey = rest_client.get_survey_details(survey_id=survey_with_question_answers)
    qid, subquestions = _subquestions(survey)
    assert subquestions

    new_text = "First option - updated"

    # Build updated props preserving all subquestions, modifying the first one
    updated_subquestions = [
        {**sq, "l10ns": {lang: {**l10n} for lang, l10n in sq["l10ns"].items()}}
        for sq in subquestions
    ]
    updated_subquestions[0]["l10ns"]["en"]["question"] = new_text

    result = rest_client.patch_survey(
        survey_id=survey_with_question_answers,
        patch_operations=[
            {
                "entity": "subquestion",
                "op": "update",
                "id": qid,
                "props": {str(i): sq for i, sq in enumerate(updated_subquestions)},
            },
        ],
    )
    assert result["operationsApplied"] == 1

    updated_survey = rest_client.get_survey_details(
        survey_id=survey_with_question_answers
    )
    _, result_subquestions = _subquestions(updated_survey)
    updated_first_sq = next(
        sq for sq in result_subquestions if sq["qid"] == subquestions[0]["qid"]
    )
    assert updated_first_sq["l10ns"]["en"]["question"] == new_text

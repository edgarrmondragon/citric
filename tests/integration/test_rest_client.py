"""Integration tests for the REST client."""

from __future__ import annotations

import contextlib
import operator
import sys
from typing import TYPE_CHECKING, Any

import pytest
import requests.exceptions
import semver

from citric.exceptions import LimeSurveyStatusError
from citric.rest import RESTClient

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:
    from collections.abc import Generator

    from citric import Client


class LegacyRESTClient(RESTClient):
    """Legacy REST client."""

    AUTH_ENDPOINT = "/rest/v1/session"

    @override
    def authenticate(self, username: str, password: str) -> None:
        """Authenticate with the REST API."""
        response = self._session.post(
            url=f"{self.url}{self.AUTH_ENDPOINT}",
            json={
                "username": username,
                "password": password,
            },
        )
        response.raise_for_status()
        self.session_id = response.json()


@pytest.fixture(scope="module")
def rest_client(
    client: Client,
    integration_url: str,
    integration_username: str,
    integration_password: str,
    server_version: semver.Version,
) -> Generator[RESTClient, None, None]:
    """LimeSurvey REST API client."""
    if server_version < (6, 2, 0):
        pytest.xfail(
            f"The REST API is not supported in LimeSurvey {server_version} < 6.2.0",
        )
    client_class = LegacyRESTClient if server_version < (6, 6, 0) else RESTClient
    with client_class(
        integration_url,
        integration_username,
        integration_password,
    ) as api_client:
        yield api_client

    with contextlib.suppress(LimeSurveyStatusError):
        for survey in client.list_surveys(integration_username):
            client.delete_survey(survey["sid"])


@pytest.mark.integration_test
def test_refresh_token(
    rest_client: RESTClient,
    server_version: semver.Version,
    request: pytest.FixtureRequest,
) -> None:
    """Test refreshing the token."""
    if server_version < (6, 6, 0):
        request.applymarker(
            pytest.mark.xfail(
                reason=(
                    "The REST API does not support refreshing the token in "
                    "LimeSurvey < 6.6.0"
                ),
                raises=requests.exceptions.HTTPError,
                strict=True,
            )
        )
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
def test_patch_survey_details(
    request: pytest.FixtureRequest,
    server_version: semver.Version,
    rest_client: RESTClient,
    survey_id: int,
) -> None:
    """Test getting surveys."""
    if (6, 15, 0) <= server_version < (6, 15, 2):
        request.applymarker(
            pytest.mark.xfail(
                reason=(
                    "Saving survey details is broken in `6.15.0` and "
                    "`6.15.1`. "
                    f"The current server version is {server_version}."
                ),
                strict=True,
            )
        )

    original = rest_client.get_survey_details(survey_id=survey_id)
    anonymized = original["anonymized"]
    token_length = original["tokenLength"]

    result = rest_client.update_survey_details(
        survey_id=survey_id,
        anonymized=not anonymized,
        tokenLength=token_length + 10,
    )
    expected = (
        True
        if server_version < semver.Version(6, 4, prerelease="dev")
        else (
            {
                "operationsApplied": 1,
                "erronousOperations": [],
            }
            if server_version < semver.Version(6, 5, prerelease="dev")
            else {
                "operationsApplied": 1,
            }
        )
    )
    assert result == expected

    updated = rest_client.get_survey_details(survey_id=survey_id)
    assert updated["anonymized"] is (not anonymized)
    assert updated["tokenLength"] == token_length + 10


@pytest.mark.integration_test
def test_update_question_answers(
    server_version: semver.Version,
    request: pytest.FixtureRequest,
    rest_client: RESTClient,
    survey_with_question_answers: int,
) -> None:
    """Test updating question answers."""
    if server_version <= (6, 2):
        request.applymarker(
            pytest.mark.xfail(
                reason=(
                    "At some point after 6.2, `questionGroups` changed from a dict "
                    "to a list. We don't bother to test for older versions."
                ),
                raises=KeyError,
                strict=True,
            )
        )

    if (6, 15, 18) <= server_version <= (6, 15, 20):
        request.applymarker(
            pytest.mark.xfail(
                reason=(
                    "PATCH for question answers is broken in 6.15.18, "
                    "6.15.19 and 6.15.20. "
                    f"The current server version is {server_version}."
                ),
                strict=True,
            )
        )

    def _question_answers(survey: dict[str, Any]) -> tuple[int | None, list]:
        for question in survey["questionGroups"][0]["questions"]:
            if answers := question.get("answers"):
                return question["qid"], answers

        return None, []

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

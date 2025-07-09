"""Integration tests for the REST client."""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Generator

import pytest
import requests
import semver

from citric._rest import RESTClient  # noqa: PLC2701
from citric.exceptions import LimeSurveyStatusError

if TYPE_CHECKING:
    from citric import Client


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
    if server_version >= (6, 15, 0):
        # TODO(edgarrmondragon): Investigate this
        # https://github.com/edgarrmondragon/citric/issues/1420
        request.applymarker(
            pytest.mark.xfail(
                reason=(
                    "The REST API seems to be broken in LimeSurvey >= 6.15.0 "
                    "and updating survey details fails with "
                    "'Failed saving general settings for survey'. "
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

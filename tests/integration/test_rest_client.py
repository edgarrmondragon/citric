"""Integration tests for the REST client."""

from __future__ import annotations

import typing as t

import pytest

from citric._rest import RESTClient  # noqa: PLC2701

if t.TYPE_CHECKING:
    import semver


@pytest.fixture(scope="module")
def rest_client(
    integration_url: str,
    integration_username: str,
    integration_password: str,
    server_version: semver.Version,
) -> t.Generator[RESTClient, None, None]:
    """LimeSurvey REST API client."""
    if server_version < (6, 0, 0):
        pytest.xfail(
            f"The REST API is not supported in LimeSurvey {server_version} < 6.0.0",
        )
    with RESTClient(
        integration_url,
        integration_username,
        integration_password,
    ) as client:
        yield client


@pytest.mark.integration_test
def test_get_surveys(rest_client: RESTClient, survey_id: int) -> None:
    """Test getting surveys."""
    surveys = rest_client.get_surveys()
    assert surveys[0]["sid"] == survey_id


@pytest.mark.integration_test
def test_get_survey_details(rest_client: RESTClient, survey_id: int) -> None:
    """Test getting surveys."""
    survey = rest_client.get_survey_details(survey_id=survey_id)
    assert survey["sid"] == survey_id


@pytest.mark.integration_test
def test_patch_survey_details(
    server_version: semver.Version,
    rest_client: RESTClient,
    survey_id: int,
) -> None:
    """Test getting surveys."""
    original = rest_client.get_survey_details(survey_id=survey_id)
    anonymized = original["anonymized"]
    token_length = original["tokenLength"]

    result = rest_client.update_survey_details(
        survey_id=survey_id,
        anonymized=not anonymized,
        tokenLength=token_length + 10,
    )
    expected = (
        {
            "operationsApplied": 1,
            "erronousOperations": [],
        }
        if server_version >= (6, 4)
        else True
    )
    assert result == expected

    updated = rest_client.get_survey_details(survey_id=survey_id)
    assert updated["anonymized"] is (not anonymized)
    assert updated["tokenLength"] == token_length + 10

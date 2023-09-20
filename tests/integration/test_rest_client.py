"""Integration tests for the REST client."""

from __future__ import annotations

import typing as t

import pytest

from citric._rest import RESTClient

if t.TYPE_CHECKING:
    import semver


@pytest.fixture(scope="module")
def rest_client(
    integration_url: str,
    integration_username: str,
    integration_password: str,
    server_version: semver.Version,
) -> RESTClient:
    """LimeSurvey REST API client."""
    if server_version < (6, 0, 0):
        pytest.xfail(
            f"The REST API is not supported in LimeSurvey {server_version} < 6.0.0",
        )
    return RESTClient(
        integration_url,
        integration_username,
        integration_password,
    )


@pytest.mark.integration_test
def test_get_surveys(rest_client: RESTClient, survey_id: int) -> None:
    """Test getting surveys."""
    surveys = rest_client.get_surveys()
    assert surveys[0]["sid"] == survey_id

"""Integration tests for the REST client."""

from __future__ import annotations

import typing as t

import pytest
import requests

from citric._rest import RESTClient

if t.TYPE_CHECKING:
    import semver


@pytest.fixture(scope="module")
def rest_client(
    integration_url: str,
    integration_username: str,
    integration_password: str,
) -> RESTClient:
    """LimeSurvey REST API client."""
    return RESTClient(
        integration_url,
        integration_username,
        integration_password,
    )


@pytest.mark.integration_test
def test_get_surveys(
    request: pytest.FixtureRequest,
    rest_client: RESTClient,
    survey_id: int,
    server_version: semver.Version,
) -> None:
    """Test getting surveys."""
    request.node.add_marker(
        pytest.mark.xfail(
            server_version < (6, 0, 0),
            reason=(
                "Quota RPC methods are not supported in LimeSurvey "
                f"{server_version} < 6.0.0"
            ),
            raises=requests.exceptions.HTTPError,
        ),
    )
    surveys = rest_client.get_surveys()
    assert surveys[0]["sid"] == survey_id

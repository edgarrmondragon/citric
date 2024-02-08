"""Integration tests configuration."""

from __future__ import annotations

import contextlib
import typing as t
from pathlib import Path

import pytest
import semver

import citric
from citric.exceptions import LimeSurveyStatusError
from tests.fixtures import MailHogClient


@pytest.fixture(scope="session")
def client(
    integration_url: str,
    integration_username: str,
    integration_password: str,
) -> t.Generator[citric.Client, None, None]:
    """RemoteControl2 API client."""
    with citric.Client(
        f"{integration_url}/index.php/admin/remotecontrol",
        integration_username,
        integration_password,
    ) as client:
        yield client

        with contextlib.suppress(LimeSurveyStatusError):
            for survey in client.list_surveys(integration_username):
                client.delete_survey(survey["sid"])


@pytest.fixture
def survey_id(client: citric.Client) -> t.Generator[int, None, None]:
    """Import a survey from a file and return its ID."""
    with Path("./examples/survey.lss").open("rb") as f:
        survey_id = client.import_survey(f, survey_id=98765)

    yield survey_id

    client.delete_survey(survey_id)


@pytest.fixture(scope="session")
def server_version(client: citric.Client) -> semver.Version:
    """Get the server version."""
    return semver.Version.parse(client.get_server_version())


@pytest.fixture(scope="session")
def database_version(client: citric.Client) -> int:
    """Get the LimeSurvey database schema version."""
    return client.get_db_version()


@pytest.fixture
def mailhog(integration_mailhog_url: str) -> MailHogClient:
    """Get the LimeSurvey database schema version."""
    client = MailHogClient(integration_mailhog_url)
    client.delete()
    return client

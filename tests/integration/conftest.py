"""Integration tests configuration."""

from __future__ import annotations

import contextlib
import hashlib
from pathlib import Path
from typing import TYPE_CHECKING

import dotenv
import pytest
import requests
import semver

import citric
from citric.exceptions import LimeSurveyStatusError
from tests.fixtures import MailpitClient

if TYPE_CHECKING:
    from collections.abc import Generator

    from pytest_docker.plugin import Services


@pytest.fixture(scope="session")
def env_file(
    tmp_path_factory: pytest.TempPathFactory,
    image_tag: str,
    integration_username: str,
    integration_password: str,
    git_reference: str | None,
    docker_context: str,
    dockerfile: str,
) -> Path:
    """Environment file."""
    tmp_path = tmp_path_factory.mktemp("integration")
    env_file = tmp_path / ".env"
    dotenv.set_key(env_file, "LS_IMAGE_TAG", image_tag)
    dotenv.set_key(env_file, "LS_USER", integration_username)
    dotenv.set_key(env_file, "LS_PASSWORD", integration_password)

    if git_reference:
        archive_url = (
            f"https://github.com/LimeSurvey/LimeSurvey/archive/{git_reference}.tar.gz"
        )
        resp = requests.get(archive_url, allow_redirects=True, timeout=5, stream=True)
        resp.raise_for_status()
        checksum = hashlib.sha256(resp.content).hexdigest()

        dotenv.set_key(env_file, "LS_REF", git_reference)
        dotenv.set_key(env_file, "LS_DOCKER_CONTEXT", docker_context)
        dotenv.set_key(env_file, "LS_DOCKERFILE", dockerfile)
        dotenv.set_key(env_file, "LS_ARCHIVE_URL", archive_url)
        dotenv.set_key(env_file, "LS_CHECKSUM", checksum)

    return env_file


@pytest.fixture(scope="session")
def docker_compose_command(env_file: Path) -> str:
    """Docker Compose command."""
    return f"docker compose --env-file {env_file}"


@pytest.fixture(scope="session")
def docker_compose_file(
    pytestconfig: pytest.Config,
    database_type: str,
    git_reference: str | None,
) -> list[Path | str] | Path | str:
    """Get an absolute path to the  `docker-compose.yml` file."""
    files = ["compose.yaml"]

    if database_type == "mysql":
        files.append("compose.mysql.yaml")

    if git_reference:
        files.append("compose.git-ref.yaml")

    return [pytestconfig.rootpath / "tests" / file for file in files]


@pytest.fixture(scope="session")
def integration_url(docker_ip: str, docker_services: Services) -> str:
    """Ensure that the service is up and responsive."""
    port = docker_services.port_for("limesurvey", 8080)
    url = f"http://{docker_ip}:{port}"

    def _check_connection() -> bool:
        try:
            return requests.get(f"{url}/index.php", timeout=5).status_code == 200
        except requests.RequestException:
            return False

    docker_services.wait_until_responsive(
        timeout=30.0,
        pause=0.1,
        check=_check_connection,
    )
    return url


@pytest.fixture(scope="session")
def integration_mailpit_url(docker_ip: str, docker_services: Services) -> str:
    """Ensure that the service is up and responsive."""
    port = docker_services.port_for("mailpit", 8025)
    url = f"http://{docker_ip}:{port}"

    def _check_connection() -> bool:
        try:
            return requests.get(f"{url}/api/v1/messages", timeout=5).status_code == 200
        except requests.RequestException:
            return False

    docker_services.wait_until_responsive(
        timeout=30.0,
        pause=0.1,
        check=_check_connection,
    )
    return url


@pytest.fixture(scope="session")
def client(
    integration_url: str,
    integration_username: str,
    integration_password: str,
) -> Generator[citric.Client, None, None]:
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
def survey_id(
    client: citric.Client,
    request: pytest.FixtureRequest,
) -> Generator[int, None, None]:
    """Import a survey from a file and return its ID."""
    with Path("./examples/survey.lss").open("rb") as f:
        survey_id = client.import_survey(f, survey_id=request.node.nodeid)

    yield survey_id

    client.delete_survey(survey_id)


@pytest.fixture(scope="session")
def server_version(client: citric.Client) -> semver.Version:
    """Get the server version."""
    return semver.Version.parse(client.get_server_version())


@pytest.fixture
def mailpit(integration_mailpit_url: str) -> MailpitClient:
    """Get the LimeSurvey database schema version."""
    client = MailpitClient(integration_mailpit_url)
    client.delete()
    return client

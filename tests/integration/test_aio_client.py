# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Integration tests for the async Python client.

The sync client seeds the server and provides the expected values.
"""

from __future__ import annotations

import csv
import io
import json
import sys
from typing import TYPE_CHECKING
from urllib.parse import quote

import anyio
import bs4
import pytest

from citric import enums
from citric.aio.client import AsyncClient
from citric.aio.transport.httpx2 import AsyncHttpx2Transport
from citric.exceptions import LimeSurveyStatusError

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Mapping
    from pathlib import Path

    import semver
    from faker import Faker

    import citric
    from citric.transport.protocol import HTTPResponse
    from citric.types import ParticipantData, QuestionsListElement
    from tests.fixtures import MailpitClient

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

pytestmark = [pytest.mark.integration_test, pytest.mark.anyio]

MIN_SERVER_VERSION = "7.0.0-alpha0"


class _RecordingTransport(AsyncHttpx2Transport):
    """Transport that records the RPC method of every request it sends."""

    def __init__(self) -> None:
        super().__init__()
        self.rpc_methods: list[str] = []

    @override
    async def request(
        self,
        method: str,
        url: str,
        *,
        data: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> HTTPResponse:
        if isinstance(data, str):
            self.rpc_methods.append(json.loads(data)["method"])
        return await super().request(method, url, data=data, headers=headers)


@pytest.fixture
def rpc_url(integration_url: str) -> str:
    """LimeSurvey RemoteControl endpoint."""
    return f"{integration_url}/index.php/admin/remotecontrol"


@pytest.fixture
async def aclient(
    rpc_url: str,
    integration_username: str,
    integration_password: str,
    server_version: semver.Version,
) -> AsyncIterator[AsyncClient]:
    """Async RemoteControl 2 API client."""
    if server_version < MIN_SERVER_VERSION:
        pytest.skip("The async client only supports LimeSurvey 7.0 and later")

    async with AsyncClient(rpc_url, integration_username, integration_password) as c:
        yield c


async def test_read_methods_match_sync_client(
    client: citric.Client,
    aclient: AsyncClient,
    survey_id: int,
    integration_username: str,
):
    """Read-only methods return what the sync client returns."""
    assert await aclient.list_surveys(integration_username) == client.list_surveys(
        integration_username,
    )
    assert await aclient.list_questions(survey_id) == client.list_questions(survey_id)
    assert await aclient.get_fieldmap(survey_id) == client.get_fieldmap(survey_id)
    assert await aclient.get_language_properties(
        survey_id,
    ) == client.get_language_properties(survey_id)
    assert await aclient.get_server_version() == client.get_server_version()


async def test_responses_round_trip(
    client: citric.Client,
    aclient: AsyncClient,
    survey_id: int,
):
    """Responses added with the async client can be exported, with Q-style keys."""
    client.activate_survey(survey_id)

    assert (
        await aclient.add_response(
            survey_id,
            {"G01Q01": "Long text 1", "G01Q02": "1", "G02Q04": "Y"},
        )
        == 1
    )
    assert await aclient.add_responses(
        survey_id,
        [
            {"G01Q01": "Long text 2", "G01Q02": "5", "G02Q04": "N"},
            {"G01Q01": "Long text 3", "G01Q02": None, "G02Q04": "Y"},
        ],
    ) == [2, 3]

    exported = await aclient.export_responses(survey_id, file_format="csv")
    assert exported == client.export_responses(survey_id, file_format="csv")

    with io.StringIO(exported.decode("utf-8-sig")) as textfile:
        rows = list(csv.DictReader(textfile, delimiter=";"))

    assert [row["G01Q01"] for row in rows] == [
        "Long text 1",
        "Long text 2",
        "Long text 3",
    ]
    assert [row["G01Q02"] for row in rows] == ["1", "5", ""]
    assert [row["G02Q04"] for row in rows] == ["Y", "N", "Y"]


async def test_concurrent_first_calls_authenticate_once(
    rpc_url: str,
    integration_username: str,
    integration_password: str,
    survey_id: int,
    server_version: semver.Version,
):
    """Concurrent first calls on a new client authenticate only once."""
    if server_version < MIN_SERVER_VERSION:
        pytest.skip("The async client only supports LimeSurvey 7.0 and later")

    transport = _RecordingTransport()
    results: list[object] = []

    async with AsyncClient(
        rpc_url,
        integration_username,
        integration_password,
        transport=transport,
    ) as new_client:

        async def fetch() -> None:
            results.append(await new_client.list_questions(survey_id))

        async with anyio.create_task_group() as tg:
            for _ in range(8):
                tg.start_soon(fetch)

    assert len(results) == 8
    assert results.count(results[0]) == 8
    assert transport.rpc_methods.count("get_session_key") == 1
    # The key is released on exit
    assert transport.rpc_methods[-1] == "release_session_key"


async def test_status_error(aclient: AsyncClient):
    """Errors reported by LimeSurvey are raised."""
    with pytest.raises(LimeSurveyStatusError, match="Error: Invalid survey"):
        await aclient.get_survey_properties(999_999_999)


@pytest.fixture
def file_upload_question(
    client: citric.Client,
    survey_id: int,
) -> QuestionsListElement:
    """Activate the survey and get its file upload question."""
    client.activate_survey(survey_id)
    groups = client.list_groups(survey_id)
    group = next(g for g in groups if g["group_name"] == "Second Group")
    questions = client.list_questions(survey_id, group["gid"])
    return next(q for q in questions if q["title"] == "G02Q03")


@pytest.fixture
def participants(faker: Faker) -> list[ParticipantData]:
    """Participants for a survey, the first two with distinct tokens."""
    return [
        {
            "email": faker.email(domain="example.com"),
            "firstname": faker.first_name(),
            "lastname": faker.last_name(),
            "token": str(token),
        }
        for token in (1, 2, 2)
    ]


@pytest.mark.parametrize(
    "by_response_id",
    [False, True],
    ids=["by_token", "by_response_id"],
)
async def test_response_files(
    client: citric.Client,
    aclient: AsyncClient,
    survey_id: int,
    file_upload_question: QuestionsListElement,
    tmp_path: Path,
    faker: Faker,
    by_response_id: bool,  # ruff: ignore[boolean-type-hint-positional-argument]
):
    """Files can be uploaded, attached to a response, iterated and downloaded."""
    token = "T00000"
    fieldname = await aclient._fieldname_from_question(file_upload_question)
    contents = [faker.zip(), faker.zip()]

    uploads = [
        await aclient.upload_file_object(
            survey_id,
            fieldname,
            f"file{i}.zip",
            io.BytesIO(content),
        )
        for i, content in enumerate(contents, start=1)
    ]

    [response_id] = await aclient.add_responses(
        survey_id,
        [
            {
                "token": token,
                fieldname: json.dumps(uploads),
                f"{fieldname}_Cfilecount": len(uploads),
            },
        ],
    )
    assert response_id == 1

    by_token = None if by_response_id else token
    by_id = response_id if by_response_id else None

    files = [
        f
        async for f in aclient.get_uploaded_file_objects(
            survey_id,
            token=by_token,
            response_id=by_id,
        )
    ]
    assert [f["meta"]["name"] for f in files] == [u["name"] for u in uploads]
    assert [f["meta"]["size"] for f in files] == [u["size"] for u in uploads]
    assert [f["content"].read() for f in files] == contents

    download_dir = tmp_path / "downloads"
    download_dir.mkdir()
    paths = await aclient.download_files(
        download_dir,
        survey_id,
        token=by_token,
        response_id=by_id,
    )

    assert [p.read_bytes() for p in paths] == contents
    # The sync client sees the same files
    assert [
        f["content"].read()
        for f in client.get_uploaded_file_objects(
            survey_id,
            token=by_token,
            response_id=by_id,
        )
    ] == contents


async def test_upload_file(
    aclient: AsyncClient,
    file_upload_question: QuestionsListElement,
    tmp_path: Path,
    faker: Faker,
):
    """A local file is uploaded with its own name, or a given one."""
    filepath = tmp_path / "file.zip"
    content = faker.zip()
    filepath.write_bytes(content)

    sid = file_upload_question["sid"]
    fieldname = await aclient._fieldname_from_question(file_upload_question)

    named = await aclient.upload_file(sid, fieldname, filepath, filename="upload.zip")
    assert named["success"]
    assert named["name"] == "upload.zip"
    assert named["ext"] == "zip"
    assert named["size"] == pytest.approx(len(content) / 1000, rel=5e-2)

    unnamed = await aclient.upload_file(sid, fieldname, filepath)
    assert unnamed["success"]
    assert unnamed["name"] == quote(filepath.name)


async def test_save_responses_and_statistics(
    aclient: AsyncClient,
    survey_id: int,
    tmp_path: Path,
):
    """Responses and statistics are exported to files."""
    await aclient.activate_survey(survey_id)
    await aclient.add_responses(
        survey_id,
        [
            {"G01Q01": "Long text 1", "G01Q02": "1", "G02Q04": "Y"},
            {"G01Q01": "Long text 2", "G01Q02": "5", "G02Q04": "N"},
        ],
    )

    responses_path = tmp_path / "responses.json"
    written = await aclient.save_responses(responses_path, survey_id)
    assert written == responses_path.stat().st_size
    assert len(json.loads(responses_path.read_bytes())["responses"]) == 2

    statistics_path = tmp_path / "statistics.html"
    written = await aclient.save_statistics(
        statistics_path,
        survey_id,
        file_format=enums.StatisticsExportFormat.HTML,
    )
    assert written == statistics_path.stat().st_size > 0

    soup = bs4.BeautifulSoup(statistics_path.read_bytes(), "html.parser")
    assert len(soup.find_all("table")) == 4  # One for each question


async def test_mail_registered_participants(
    client: citric.Client,
    aclient: AsyncClient,
    survey_id: int,
    participants: list[ParticipantData],
    mailpit: MailpitClient,
):
    """Participants are added and emailed, and the emails are delivered."""
    client.activate_survey(survey_id)
    client.activate_tokens(survey_id, [1, 2])
    await aclient.add_participants(
        survey_id,
        participant_data=participants,
        create_tokens=False,
    )

    assert mailpit.get_all()["total"] == 0

    outcome = await aclient.mail_registered_participants(survey_id)
    assert outcome == {
        "status": "0 left to send",
        "1": {
            "name": f"{participants[0]['firstname']} {participants[0]['lastname']}",
            "email": participants[0]["email"],
            "status": "OK",
            "warning": None,
            "error": None,
        },
        "2": {
            "name": f"{participants[1]['firstname']} {participants[1]['lastname']}",
            "email": participants[1]["email"],
            "status": "OK",
            "warning": None,
            "error": None,
        },
    }
    assert mailpit.get_all()["total"] == 2

    mailpit.delete()

    with pytest.raises(LimeSurveyStatusError, match="Error: No candidate tokens"):
        await aclient.mail_registered_participants(survey_id)

    assert mailpit.get_all()["total"] == 0

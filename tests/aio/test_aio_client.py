# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Tests for the async API client."""

from __future__ import annotations

import io
from typing import TYPE_CHECKING

import anyio
import pytest

from citric.aio.client import AsyncClient
from citric.aio.transport.httpx2 import AsyncHttpx2Transport
from citric.exceptions import LimeSurveyStatusError
from tests.aio.conftest import SESSION_KEY, RPCServer

if TYPE_CHECKING:
    from collections.abc import AsyncIterator
    from pathlib import Path

pytestmark = pytest.mark.anyio

QUESTIONS = [
    {"qid": 11, "sid": 123, "gid": 4, "title": "Q1"},
    {"qid": 12, "sid": 123, "gid": 4, "title": "Q2"},
]


@pytest.fixture
async def client(server: RPCServer) -> AsyncIterator[AsyncClient]:
    """An async client that is closed after the test."""
    async with AsyncClient(server.url, "user", "password") as client:
        yield client


async def test_creating_a_client_does_not_contact_the_server(server: RPCServer):
    """Authentication is deferred until the first request."""
    client = AsyncClient(server.url, "user", "password")
    assert server.calls == []
    await client.aclose()
    assert client.session.closed


async def test_passthrough_method(server: RPCServer, client: AsyncClient):
    """A generated wrapper sends the session key and its arguments."""
    server.results["list_surveys"] = [{"sid": 1}]

    assert await client.list_surveys("someone", survey_group_id=3) == [{"sid": 1}]
    assert server.calls[-1] == ("list_surveys", [SESSION_KEY, "someone", 3])


async def test_concurrent_calls_authenticate_once(
    server: RPCServer, client: AsyncClient
):
    """Tasks sharing a new client authenticate only once."""
    server.auth_delay = 0.3

    async with anyio.create_task_group() as tg:
        for _ in range(5):
            tg.start_soon(client.list_surveys)

    assert server.methods().count("get_session_key") == 1
    assert server.methods().count("list_surveys") == 5


async def test_add_response_maps_question_codes(server: RPCServer, client: AsyncClient):
    """Question titles are mapped to Q-style field names."""
    server.results["list_questions"] = QUESTIONS
    server.results["add_response"] = "42"

    assert await client.add_response(123, {"Q1": "yes", "other": "x"}) == 42

    assert server.calls[-1] == (
        "add_response",
        [SESSION_KEY, 123, {"Q11": "yes", "other": "x"}],
    )
    # The server version doesn't matter, so it isn't requested
    assert "get_site_settings" not in server.methods()


async def test_add_responses(server: RPCServer, client: AsyncClient):
    """Several responses are added in order, after a single question lookup."""
    server.results["list_questions"] = QUESTIONS
    server.results["add_response"] = "7"

    assert await client.add_responses(123, [{"Q1": "a"}, {"Q2": "b"}]) == [7, 7]

    assert server.methods().count("list_questions") == 1
    added = [params for method, params in server.calls if method == "add_response"]
    assert added == [
        [SESSION_KEY, 123, {"Q11": "a"}],
        [SESSION_KEY, 123, {"Q12": "b"}],
    ]


async def test_export_responses(server: RPCServer, client: AsyncClient):
    """The base64 payload is decoded."""
    server.results["export_responses"] = "aGVsbG8="  # hello

    assert await client.export_responses(123) == b"hello"
    assert server.calls[-1][0] == "export_responses"

    server.results["export_responses_by_token"] = "d29ybGQ="  # world
    assert await client.export_responses(123, token="abc") == b"world"
    assert server.calls[-1][0] == "export_responses_by_token"


async def test_save_responses(server: RPCServer, client: AsyncClient, tmp_path: Path):
    """Exported responses are written to disk."""
    server.results["export_responses"] = "aGVsbG8="
    target = tmp_path / "responses.json"

    assert await client.save_responses(target, 123) == 5
    assert target.read_bytes() == b"hello"


async def test_custom_transport(server: RPCServer):
    """The given transport is used, and closed with the client."""
    transport = AsyncHttpx2Transport()

    async with AsyncClient(
        server.url, "user", "password", transport=transport
    ) as client:
        await client.list_surveys()

    assert transport._client.is_closed


UPLOADED_FILES = {
    "one": {"meta": {"filename": "a.txt"}, "content": "YWFh"},  # aaa
    "two": {"meta": {"filename": "b.txt"}, "content": "YmJi"},  # bbb
}


async def test_get_uploaded_file_objects(server: RPCServer, client: AsyncClient):
    """Uploaded files are yielded asynchronously, with decoded contents."""
    server.results["get_uploaded_files"] = UPLOADED_FILES

    files = [f async for f in client.get_uploaded_file_objects(123, token="abc")]

    assert [f["meta"]["filename"] for f in files] == ["a.txt", "b.txt"]
    assert [f["content"].read() for f in files] == [b"aaa", b"bbb"]
    assert server.calls[-1] == ("get_uploaded_files", [SESSION_KEY, 123, "abc", None])


async def test_download_files(server: RPCServer, client: AsyncClient, tmp_path: Path):
    """Uploaded files are written to a directory."""
    server.results["get_uploaded_files"] = UPLOADED_FILES

    paths = await client.download_files(tmp_path, 123, response_id=9)

    assert paths == [tmp_path / "a.txt", tmp_path / "b.txt"]
    assert [p.read_bytes() for p in paths] == [b"aaa", b"bbb"]


async def test_save_statistics(server: RPCServer, client: AsyncClient, tmp_path: Path):
    """Exported statistics are written to disk."""
    server.results["export_statistics"] = "aGVsbG8="
    target = tmp_path / "stats.pdf"

    assert await client.save_statistics(target, 123, graph=True) == 5
    assert target.read_bytes() == b"hello"
    assert server.calls[-1] == (
        "export_statistics",
        [SESSION_KEY, 123, "pdf", None, "yes", None],
    )


async def test_upload_file(server: RPCServer, client: AsyncClient, tmp_path: Path):
    """A local file is read and uploaded with its name, or a given one."""
    path = tmp_path / "data.bin"
    path.write_bytes(b"hello")
    server.results["upload_file"] = {"success": True}

    await client.upload_file(123, "Q1_file", path)
    await client.upload_file(123, "Q1_file", path, filename="other.bin")

    uploads = [params for method, params in server.calls if method == "upload_file"]
    assert uploads == [
        [SESSION_KEY, 123, "Q1_file", "data.bin", "aGVsbG8="],
        [SESSION_KEY, 123, "Q1_file", "other.bin", "aGVsbG8="],
    ]


async def test_import_survey_from_file_object(server: RPCServer, client: AsyncClient):
    """File objects are base64 encoded."""
    server.results["import_survey"] = 777

    assert await client.import_survey(io.BytesIO(b"hello")) == 777
    assert server.calls[-1][0] == "import_survey"
    assert server.calls[-1][1][:2] == [SESSION_KEY, "aGVsbG8="]


async def test_invite_participants(server: RPCServer, client: AsyncClient):
    """The number of emails left to send is parsed from the status."""
    server.results["invite_participants"] = {"status": "3 left to send"}

    assert await client.invite_participants(123) == 3


async def test_invite_participants_error(server: RPCServer, client: AsyncClient):
    """Error statuses are raised."""
    server.results["invite_participants"] = {"status": "Error: nope"}

    with pytest.raises(LimeSurveyStatusError, match="Error: nope"):
        await client.invite_participants(123)

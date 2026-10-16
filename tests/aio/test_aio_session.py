# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Tests for the async RPC session."""

from __future__ import annotations

import json
import time
from typing import TYPE_CHECKING, Any

import anyio
import pytest
from werkzeug.wrappers import Response

from citric.aio.session import AsyncSession
from citric.aio.transport.httpx2 import AsyncHttpx2Transport
from citric.exceptions import (
    InvalidJSONResponseError,
    LimeSurveyApiError,
    LimeSurveyStatusError,
    ResponseMismatchError,
)

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Callable

    from pytest_httpserver import HTTPServer
    from werkzeug.wrappers import Request

pytestmark = pytest.mark.anyio

SESSION_KEY = "async-session-key"


class RPCServer:
    """A minimal LSRC2 responder that records the calls it receives."""

    def __init__(self, httpserver: HTTPServer) -> None:
        self.calls: list[tuple[str, list[Any]]] = []
        self.auth_delay = 0.0
        self.overrides: dict[str, Callable[[int], Response]] = {}
        httpserver.expect_request("/", method="POST").respond_with_handler(self.handle)
        self.url = httpserver.url_for("/")

    def handle(self, request: Request) -> Response:
        """Serve one RPC request."""
        payload = request.json
        method, params, request_id = payload["method"], payload["params"], payload["id"]
        self.calls.append((method, params))

        if method in self.overrides:
            return self.overrides[method](request_id)

        if method == "get_session_key":
            time.sleep(self.auth_delay)
            result: Any = SESSION_KEY
        else:
            result = "OK"

        return self.reply(request_id, result)

    @staticmethod
    def reply(
        request_id: int,
        result: Any = None,  # ruff: ignore[any-type]
        error: Any = None,  # ruff: ignore[any-type]
    ) -> Response:
        """Build a JSON-RPC response."""
        return Response(
            json.dumps({"id": request_id, "result": result, "error": error}),
            content_type="application/json",
        )

    def methods(self) -> list[str]:
        """Names of the methods called so far."""
        return [method for method, _ in self.calls]


@pytest.fixture
def server(httpserver: HTTPServer) -> RPCServer:
    """A recording RPC server."""
    return RPCServer(httpserver)


@pytest.fixture
async def session(server: RPCServer) -> AsyncIterator[AsyncSession]:
    """An async session that is closed after the test."""
    async with AsyncSession(server.url, "user", "password") as session:
        yield session


async def test_creating_a_session_does_not_contact_the_server(server: RPCServer):
    """Authentication is deferred until the key is first needed."""
    session = AsyncSession(server.url, "user", "password")
    assert server.calls == []
    assert not session.closed
    await session.aclose()
    assert server.calls == []
    assert session.closed


async def test_rpc_authenticates_and_passes_key(
    server: RPCServer,
    session: AsyncSession,
):
    """The first call authenticates, and later ones send the key."""
    assert await session.list_surveys("someone") == "OK"
    assert await session.get_key() == SESSION_KEY

    assert server.calls == [
        ("get_session_key", ["user", "password", "Authdb"]),
        ("list_surveys", [SESSION_KEY, "someone"]),
    ]


async def test_system_methods_do_not_authenticate(
    server: RPCServer,
    session: AsyncSession,
):
    """``system.*`` methods are sent without a session key."""
    await session.system.listMethods()
    assert server.calls == [("system.listMethods", [])]


async def test_auth_plugin(server: RPCServer):
    """The auth plugin is sent to get_session_key."""
    async with AsyncSession(server.url, "u", "p", auth_plugin="AuthLDAP") as session:
        await session.get_key()

    assert server.calls[0] == ("get_session_key", ["u", "p", "AuthLDAP"])


async def test_concurrent_first_calls_authenticate_once(
    server: RPCServer,
    session: AsyncSession,
):
    """Tasks sharing a new session authenticate only once."""
    server.auth_delay = 0.3
    results: list[Any] = []

    async def call() -> None:
        results.append(await session.list_surveys())

    async with anyio.create_task_group() as tg:
        for _ in range(8):
            tg.start_soon(call)

    assert results == ["OK"] * 8
    assert server.methods().count("get_session_key") == 1
    assert server.methods().count("list_surveys") == 8


async def test_failed_authentication_can_be_retried(server: RPCServer):
    """A failed login leaves the session usable for another attempt."""
    server.overrides["get_session_key"] = lambda i: server.reply(
        i,
        {"status": "Invalid user name or password"},
    )

    async with AsyncSession(server.url, "user", "wrong") as session:
        with pytest.raises(LimeSurveyStatusError, match="Invalid user name"):
            await session.get_key()

        del server.overrides["get_session_key"]
        assert await session.get_key() == SESSION_KEY

    assert server.methods() == [
        "get_session_key",
        "get_session_key",
        "release_session_key",
    ]


async def test_aclose_releases_the_key_once(server: RPCServer):
    """Closing releases the key, and closing again does nothing."""
    session = AsyncSession(server.url, "user", "password")
    await session.get_key()

    await session.aclose()
    await session.aclose()

    assert session.closed
    assert server.calls[-1] == ("release_session_key", [SESSION_KEY])
    assert server.methods().count("release_session_key") == 1


async def test_context_manager_closes(server: RPCServer):
    """Leaving the context closes the session, even on error."""

    async def use_and_fail() -> None:
        async with AsyncSession(server.url, "user", "password") as session:
            sessions.append(session)
            await session.get_key()
            raise ZeroDivisionError

    sessions: list[AsyncSession] = []
    with pytest.raises(ZeroDivisionError):
        await use_and_fail()

    assert sessions[0].closed
    assert server.methods()[-1] == "release_session_key"


async def test_aclose_closes_transport_when_release_fails(server: RPCServer):
    """The session is closed and the transport released if the release fails."""
    server.overrides["release_session_key"] = lambda i: server.reply(i, error="boom")
    transport = AsyncHttpx2Transport()
    session = AsyncSession(server.url, "user", "password", transport=transport)
    await session.get_key()

    with pytest.raises(LimeSurveyApiError, match="boom"):
        await session.aclose()

    assert session.closed
    assert transport._client.is_closed


async def test_aclose_waits_for_in_flight_authentication(server: RPCServer):
    """A key being retrieved while closing is released."""
    server.auth_delay = 0.3
    session = AsyncSession(server.url, "user", "password")

    async with anyio.create_task_group() as tg:
        tg.start_soon(session.get_key)
        await anyio.sleep(0.1)
        await session.aclose()

    assert server.methods() == ["get_session_key", "release_session_key"]


async def test_cancelled_authentication_can_be_retried(server: RPCServer):
    """Cancelling a task mid-login doesn't poison the session."""
    server.auth_delay = 0.5
    session = AsyncSession(server.url, "user", "password")

    with anyio.move_on_after(0.1):
        await session.get_key()

    server.auth_delay = 0
    assert await session.get_key() == SESSION_KEY
    await session.aclose()


async def test_api_error(server: RPCServer, session: AsyncSession):
    """A non-null error raises LimeSurveyApiError."""
    server.overrides["boom"] = lambda i: server.reply(i, error="API Error!")
    with pytest.raises(LimeSurveyApiError, match="API Error!"):
        await session.boom()


async def test_status_error(server: RPCServer, session: AsyncSession):
    """A result with a status other than OK raises LimeSurveyStatusError."""
    server.overrides["boom"] = lambda i: server.reply(
        i, {"status": "Status Error!", "error_code": 7}
    )
    with pytest.raises(LimeSurveyStatusError, match="Status Error!"):
        await session.boom()


async def test_http_error(server: RPCServer, session: AsyncSession):
    """An HTTP error status raises LimeSurveyApiError."""
    server.overrides["boom"] = lambda _: Response("nope", status=500)
    with pytest.raises(LimeSurveyApiError, match="status 500"):
        await session.boom()


async def test_invalid_json(server: RPCServer, session: AsyncSession):
    """A non-JSON body raises InvalidJSONResponseError."""
    server.overrides["boom"] = lambda _: Response("not json")
    with pytest.raises(InvalidJSONResponseError):
        await session.boom()


async def test_response_id_mismatch(server: RPCServer, session: AsyncSession):
    """A response to another request raises ResponseMismatchError."""
    server.overrides["boom"] = lambda i: server.reply(i + 1, "OK")
    with pytest.raises(ResponseMismatchError):
        await session.boom()

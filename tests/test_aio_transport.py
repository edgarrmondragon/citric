# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Tests for the async transport protocol."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import anyio
import pytest
from werkzeug.wrappers import Response

from citric.aio.transport.httpx2 import AsyncHttpx2Transport
from citric.aio.transport.protocol import AsyncHTTPTransport

if TYPE_CHECKING:
    from collections.abc import Mapping

    from pytest_httpserver import HTTPServer
    from werkzeug.wrappers import Request

    from citric.transport.protocol import HTTPResponse


class _GoodTransport:
    async def request(
        self,
        method: str,
        url: str,
        *,
        data: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> HTTPResponse:
        raise NotImplementedError

    async def aclose(self) -> None:
        pass


class _SyncCloseTransport:
    """Has the sync ``close`` of the sync protocol, not ``aclose``."""

    async def request(self, method: str, url: str) -> HTTPResponse:
        raise NotImplementedError

    def close(self) -> None:
        pass


def test_object_with_request_and_aclose_satisfies_protocol():
    """Anything with ``request`` and ``aclose`` is an AsyncHTTPTransport."""
    assert isinstance(_GoodTransport(), AsyncHTTPTransport)


def test_sync_transport_shape_does_not_satisfy_protocol():
    """An object with only the sync ``close`` isn't an AsyncHTTPTransport."""
    assert not isinstance(_SyncCloseTransport(), AsyncHTTPTransport)


def test_httpx2_transport_satisfies_protocol():
    """AsyncHttpx2Transport is an AsyncHTTPTransport."""
    assert isinstance(AsyncHttpx2Transport(), AsyncHTTPTransport)


def echo_handler(request: Request) -> Response:
    """Echo the request body, method and a header back as JSON."""
    return Response(
        json.dumps(
            {
                "body": request.get_data(as_text=True),
                "method": request.method,
                "header": request.headers.get("X-Test"),
            },
        ),
        content_type="application/json",
    )


@pytest.mark.anyio
async def test_httpx2_transport_request(httpserver: HTTPServer):
    """A request goes over the network, and the response body is already read."""
    httpserver.expect_request("/", method="POST").respond_with_handler(echo_handler)

    transport = AsyncHttpx2Transport()
    try:
        response = await transport.request(
            "POST",
            httpserver.url_for("/"),
            data="payload",
            headers={"X-Test": "yes"},
        )
    finally:
        await transport.aclose()

    assert response.status_code == 200
    assert response.json() == {"body": "payload", "method": "POST", "header": "yes"}


@pytest.mark.anyio
async def test_httpx2_transport_concurrent_requests(httpserver: HTTPServer):
    """One transport serves concurrent requests."""
    httpserver.expect_request("/", method="POST").respond_with_handler(echo_handler)

    results: list[str] = []
    transport = AsyncHttpx2Transport(max_connections=4)
    try:
        async with anyio.create_task_group() as tg:

            async def post(n: int) -> None:
                response = await transport.request(
                    "POST",
                    httpserver.url_for("/"),
                    data=str(n),
                )
                results.append(response.json()["body"])

            for n in range(8):
                tg.start_soon(post, n)
    finally:
        await transport.aclose()

    assert sorted(results) == [str(n) for n in range(8)]


@pytest.mark.anyio
async def test_httpx2_transport_closed(httpserver: HTTPServer):
    """Requests on a closed transport fail."""
    transport = AsyncHttpx2Transport()
    await transport.aclose()

    with pytest.raises(RuntimeError):
        await transport.request("POST", httpserver.url_for("/"))

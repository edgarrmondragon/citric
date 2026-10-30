# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Citric async transport protocol implementation for httpx2."""

from __future__ import annotations

__lazy_modules__ = {
    "httpx2",
}

from typing import TYPE_CHECKING

import httpx2

if TYPE_CHECKING:
    from collections.abc import Mapping

    from citric.transport.protocol import HTTPResponse

__all__ = [
    "AsyncHttpx2Transport",
]


class AsyncHttpx2Transport:
    """Citric async transport protocol implementation for httpx2.

    Requires the `httpx2 <https://github.com/pydantic/httpx2>`_ package,
    which is not installed by citric itself: run ``pip install httpx2``.

    Wraps :py:class:`httpx2.AsyncClient <httpx2.AsyncClient>`.

    Args:
        max_connections: Maximum number of concurrent connections, or ``None`` for no
            limit. Requests above this number wait for a free connection.
        max_keepalive_connections: Maximum number of idle connections to keep alive,
            or ``None`` for no limit. Set it to at least the number of concurrent
            requests to reuse connections between requests.
        keepalive_expiry: Seconds to keep idle connections alive, or ``None`` for no
            limit.

    .. versionadded:: NEXT_VERSION
    """

    def __init__(
        self,
        *,
        max_connections: int | None = 100,
        max_keepalive_connections: int | None = 20,
        keepalive_expiry: float | None = 5.0,
    ) -> None:
        """Initialize the async httpx2 transport."""
        self._client = httpx2.AsyncClient(
            limits=httpx2.Limits(
                max_connections=max_connections,
                max_keepalive_connections=max_keepalive_connections,
                keepalive_expiry=keepalive_expiry,
            ),
        )

    async def request(
        self,
        method: str,
        url: str,
        *,
        data: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> HTTPResponse:
        """Send an HTTP request.

        Args:
            method: The HTTP method.
            url: The server URL.
            data: The request body.
            headers: The HTTP headers.

        Returns:
            A response object, with its body already read.
        """
        return await self._client.request(
            method=method,
            url=url,
            content=data,
            headers=headers,
        )

    async def aclose(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

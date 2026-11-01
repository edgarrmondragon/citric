# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Asynchronous HTTP transport abstraction.

The asynchronous counterpart of :mod:`citric.transport.protocol`:
:class:`AsyncHTTPTransport` captures the slice of an async HTTP client that citric
needs, so anything with a compatible ``request``/``aclose`` shape can be passed in as
``transport``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Mapping

    from citric.transport.protocol import HTTPResponse

__all__ = [
    "AsyncHTTPTransport",
]


@runtime_checkable
class AsyncHTTPTransport(Protocol):
    """The subset of an async HTTP client that citric relies on.

    Responses are the same as for :class:`~citric.transport.protocol.HTTPTransport`:
    once :meth:`request` has returned, the body is fully read, so decoding it with
    :meth:`~citric.transport.protocol.HTTPResponse.json` doesn't need to be awaited.

    .. versionadded:: NEXT_VERSION
    """

    async def request(
        self,
        method: str,
        url: str,
        *,
        data: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> HTTPResponse:
        """Send an HTTP request."""
        ...

    async def aclose(self) -> None:
        """Release any resources held by the transport."""
        ...

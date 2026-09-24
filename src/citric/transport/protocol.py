# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""HTTP transport abstraction.

Citric only needs a very small slice of an HTTP client's behavior to talk to
the LimeSurvey RPC endpoint: issue a POST request with a body and headers, and
close any underlying connections when the session ends. :class:`HTTPTransport`
captures that slice as a :class:`~typing.Protocol`, so anything with a
compatible ``request``/``close`` shape can be passed in as ``requests_session``,
not just a :py:class:`requests.Session <requests.Session>`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Mapping

__all__ = [
    "HTTPResponse",
    "HTTPTransport",
]


@runtime_checkable
class HTTPResponse(Protocol):
    """The subset of a response object that citric relies on."""

    @property
    def content(self) -> bytes:
        """The response body."""
        ...

    @property
    def status_code(self) -> int:
        """The HTTP status of this response."""
        ...

    def json(self) -> Any:  # ruff: ignore[any-type]
        """Decode the response body as JSON."""
        ...


@runtime_checkable
class HTTPTransport(Protocol):
    """The subset of an HTTP client that citric relies on.

    :py:class:`requests.Session <requests.Session>` satisfies this protocol
    as-is. For other HTTP client libraries, use one of the adapters in
    :mod:`citric.transport`, such as
    :class:`citric.transport.httpx2.Httpx2Transport` or
    :class:`citric.transport.urllib3.Urllib3Transport`, or write
    your own.

    .. versionadded:: NEXT_VERSION
    """

    def request(
        self,
        method: str,
        url: str,
        *,
        data: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> HTTPResponse:
        """Send an HTTP request."""
        ...

    def close(self) -> None:
        """Release any resources held by the transport."""
        ...

# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Citric transport protocol implementation for urllib3."""

from __future__ import annotations

__lazy_modules__ = {
    "json",
    "urllib3",
    "urllib3.response",
}

from typing import TYPE_CHECKING, Any

import urllib3
import urllib3.response

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from citric.transport.protocol import HTTPResponse

__all__ = [
    "Urllib3Transport",
]


class Urllib3ResponseWrapper:
    """A urllib3 response object wrapper used for protocol compatibility.

    .. versionadded:: NEXT_VERSION
    """

    def __init__(self, response: urllib3.response.BaseHTTPResponse) -> None:
        self._response = response

    @property
    def status_code(self) -> int:
        """The HTTP status of this response."""
        return self._response.status

    def json(self) -> Any:  # ruff: ignore[any-type]
        """The JSON data contained in the response.

        Returns:
            JSON data.
        """
        return self._response.json()


class Urllib3Transport:
    """Citric transport protocol implementation for urllib3.

    Backed by the `urllib3 <https://urllib3.readthedocs.io>`_ package, which is
    installed with citric, so there's nothing else to install.

    Wraps :py:class:`urllib3.PoolManager <urllib3.PoolManager>`.

    Args:
        num_pools: Number of connection pools to cache, one per host.
        maxsize: Maximum number of connections to keep alive in each pool. Set it to
            at least the number of threads sharing the transport, otherwise
            connections above this number are discarded after use.
        block: Whether to block when a pool has ``maxsize`` connections in use,
            instead of opening additional, non-reusable ones.
        pool_timeout: If set and the pool is set to ``block=True``, then this method
            will block for ``pool_timeout`` seconds and raise an exception if no
            connection is available within the time period. Set it to avoid hanging
            indefinitely while requests are waiting for a pool slot.
        **pool_kwargs: Additional keyword arguments passed to
            :py:class:`urllib3.PoolManager <urllib3.PoolManager>`, e.g. ``timeout``
            or ``retries``.

    .. versionadded:: NEXT_VERSION
    """

    def __init__(
        self,
        *,
        num_pools: int = 10,
        maxsize: int = 1,
        block: bool = False,
        pool_timeout: int | None = None,
        **pool_kwargs: Any,
    ) -> None:
        """Initialize the urllib3 transport."""
        self._pool = urllib3.PoolManager(
            num_pools=num_pools,
            maxsize=maxsize,
            block=block,
            **pool_kwargs,
        )
        self._pool_timeout = pool_timeout

    def request(
        self,
        method: str,
        url: str,
        *,
        data: str | bytes | Iterable[bytes] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> HTTPResponse:
        """Send an HTTP request.

        Args:
            method: The HTTP method.
            url: The server URL.
            data: The request body.
            headers: The HTTP headers.

        Returns:
            A response object.
        """
        return Urllib3ResponseWrapper(
            self._pool.request(
                method=method,
                url=url,
                body=data,
                headers=headers,
                pool_timeout=self._pool_timeout,
            )
        )

    def close(self) -> None:
        """Close the HTTP session."""
        self._pool.clear()

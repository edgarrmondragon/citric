# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Citric transport protocol implementation for httpx2."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx2

if TYPE_CHECKING:
    from collections.abc import Mapping

__all__ = [
    "Httpx2Transport",
]


class Httpx2Transport:
    """Citric transport protocol implementation for httpx2.

    Requires the `httpx2 <https://github.com/pydantic/httpx2>`_ package,
    which is not installed by citric itself: run ``pip install httpx2``.

    .. versionadded:: NEXT_VERSION
    """

    def __init__(self) -> None:
        """Initialize the httpx2 transport."""
        self._client = httpx2.Client()

    def post(
        self,
        url: str,
        *,
        data: str,
        headers: Mapping[str, str],
    ) -> httpx2.Response:
        """Send a POST HTTP request.

        Args:
            url: The server URL.
            data: The request body.
            headers: The HTTP headers.

        Returns:
            A response object.
        """
        return self._client.post(url=url, content=data, headers=headers)

    def close(self) -> None:
        """Close the HTTP session."""
        self._client.close()

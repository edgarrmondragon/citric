# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Citric transport protocol implementation for urllib3."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import urllib3
import urllib3.response

if TYPE_CHECKING:
    from collections.abc import Mapping


class Urllib3ResponseWrapper:
    """A urllib3 response object wrapper used for protocol compatibility.

    .. versionadded:: NEXT_VERSION
    """

    def __init__(self, response: urllib3.response.BaseHTTPResponse) -> None:
        self._response = response

    @property
    def content(self) -> bytes:
        """The raw response bytes."""
        return self._response.data

    @property
    def status_code(self) -> int:
        """The HTTP status of this response."""
        return self._response.status

    def json(self) -> Any:  # ruff: ignore[any-type]
        """The JSON data contained in the response.

        Returns:
            JSON data.
        """
        return json.loads(self._response.data.decode("utf-8"))


class Urllib3Transport:
    """Citric transport protocol implementation for urllib3.

    Requires the `urllib3 <https://urllib3.readthedocs.io>`_ package.
    ``urllib3`` is usually already installed as a dependency of ``requests``,
    but isn't a direct dependency of citric itself, so pin it explicitly
    (``pip install urllib3``) if you don't want to rely on that.

    .. versionadded:: NEXT_VERSION
    """

    def __init__(self) -> None:
        """Initialize the urllib3 transport."""
        self._pool = urllib3.PoolManager()

    def post(
        self,
        url: str,
        *,
        data: str,
        headers: Mapping[str, str],
    ) -> Urllib3ResponseWrapper:
        """Send a POST HTTP request.

        Args:
            url: The server URL.
            data: The request body.
            headers: The HTTP headers.

        Returns:
            A response object.
        """
        return Urllib3ResponseWrapper(
            self._pool.request(
                method="POST",
                url=url,
                body=data,
                headers=headers,
            )
        )

    def close(self) -> None:
        """Close the HTTP session."""
        self._pool.clear()

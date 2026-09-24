# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Citric transport protocol implementation for httpx2."""

from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Mapping

    from citric.transport.protocol import HTTPResponse

__all__ = [
    "StdlibTransport",
]


@dataclass
class StdlibResponseWrapper:
    """A urllib.request response object wrapper used for protocol compatibility.

    .. versionadded:: NEXT_VERSION
    """

    content: bytes
    """The raw response bytes."""

    status_code: int
    """The HTTP status of this response."""

    def json(self) -> Any:  # ruff: ignore[any-type]
        """The JSON data contained in the response.

        Returns:
            JSON data.
        """
        return json.loads(self.content)


class StdlibTransport:
    """Citric transport protocol implementation for Python's ``urllib.request``.

    .. versionadded:: NEXT_VERSION
    """

    def request(  # ruff: ignore[no-self-use]
        self,
        method: str,
        url: str,
        *,
        data: str,
        headers: Mapping[str, str],
    ) -> HTTPResponse:
        """Send a POST HTTP request.

        Args:
            method: The HTTP method.
            url: The server URL.
            data: The request body.
            headers: The HTTP headers.

        Returns:
            A response object.
        """
        req = urllib.request.Request(  # ruff: ignore[suspicious-url-open-usage]
            url,
            method=method,
            data=data.encode(),
            headers=headers,
        )
        with urllib.request.urlopen(req) as f:  # ruff: ignore[suspicious-url-open-usage]
            return StdlibResponseWrapper(content=f.read(), status_code=f.status)

    def close(self) -> None:
        """Close the HTTP session."""

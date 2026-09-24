# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Citric transport protocol implementation for httpx2."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import httpx2

if TYPE_CHECKING:
    from collections.abc import Mapping


class Httpx2ResponseWrapper:
    """An httpx2 response object wrapper used for protocol compatibility.

    .. versionadded:: NEXT_VERSION
    """

    def __init__(self, response: httpx2.Response) -> None:
        self._response = response

    @property
    def content(self) -> bytes:
        """The raw response bytes."""
        return self._response.content

    def json(self) -> Any:  # ruff: ignore[any-type]
        """The JSON data contained in the response.

        Returns:
            JSON data.
        """
        return self._response.json()

    def raise_for_status(self) -> None:
        """Raise an exception if the response has an HTTP error status."""
        self._response.raise_for_status()


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
    ) -> Httpx2ResponseWrapper:
        """Send a POST HTTP request.

        Args:
            url: The server URL.
            data: The request body.
            headers: The HTTP headers.

        Returns:
            A response object.
        """
        return Httpx2ResponseWrapper(
            self._client.post(
                url=url,
                content=data,
                headers=headers,
            )
        )

    def close(self) -> None:
        """Close the HTTP session."""
        self._client.close()

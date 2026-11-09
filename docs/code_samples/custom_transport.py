# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Example of a minimal custom HTTP transport built on the standard library."""

# ruff: file-ignore[any-type, docstring-missing-returns, no-self-use]

from __future__ import annotations

# start example
import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from citric import Client

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping


@dataclass
class StdlibResponse:
    """A response that satisfies `citric.transport.protocol.HTTPResponse`."""

    status_code: int
    content: bytes

    def json(self) -> Any:
        """Decode the response body as JSON."""
        return json.loads(self.content)


class StdlibTransport:
    """A transport that satisfies `citric.transport.protocol.HTTPTransport`."""

    def request(
        self,
        method: str,
        url: str,
        *,
        data: str | bytes | Iterable[bytes] | None = None,
        headers: Mapping[str, str] | None = None,
        timeout: float | None = None,
    ) -> StdlibResponse:
        """Send an HTTP request."""
        body = data.encode() if isinstance(data, str) else data
        req = urllib.request.Request(  # ruff: ignore[suspicious-url-open-usage]
            url,
            data=body,
            headers=dict(headers or {}),
            method=method,
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:  # ruff: ignore[suspicious-url-open-usage]
                return StdlibResponse(resp.status, resp.read())
        except urllib.error.HTTPError as e:
            return StdlibResponse(e.code, e.read())

    def close(self) -> None:
        """Release any resources. This transport holds none."""


client = Client(
    "https://example.com/index.php/admin/remotecontrol",
    "iamadmin",
    "secret",
    transport=StdlibTransport(),
)
# end example

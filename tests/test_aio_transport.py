# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Tests for the async transport protocol."""

from __future__ import annotations

from typing import TYPE_CHECKING

from citric.aio.transport.protocol import AsyncHTTPTransport

if TYPE_CHECKING:
    from collections.abc import Mapping

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

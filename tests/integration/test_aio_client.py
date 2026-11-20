# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Integration tests for async-only behavior of the async Python client.

The RPC methods themselves are covered by ``test_rpc_client.py``, which runs against
both clients.
"""

from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING

import anyio
import pytest

from citric.aio.client import AsyncClient
from citric.aio.transport.httpx2 import AsyncHttpx2Transport

if TYPE_CHECKING:
    from collections.abc import Mapping

    from citric.transport.protocol import HTTPResponse

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

pytestmark = [pytest.mark.integration_test, pytest.mark.anyio]


class _RecordingTransport(AsyncHttpx2Transport):
    """Transport that records the RPC method of every request it sends."""

    def __init__(self) -> None:
        super().__init__()
        self.rpc_methods: list[str] = []

    @override
    async def request(
        self,
        method: str,
        url: str,
        *,
        data: str | None = None,
        headers: Mapping[str, str] | None = None,
        timeout: float | None = None,
    ) -> HTTPResponse:
        if isinstance(data, str):
            self.rpc_methods.append(json.loads(data)["method"])
        return await super().request(
            method,
            url,
            data=data,
            headers=headers,
            timeout=timeout,
        )


@pytest.fixture
def rpc_url(integration_url: str) -> str:
    """LimeSurvey RemoteControl endpoint."""
    return f"{integration_url}/index.php/admin/remotecontrol"


async def test_concurrent_first_calls_authenticate_once(
    rpc_url: str,
    integration_username: str,
    integration_password: str,
    survey_id: int,
):
    """Concurrent first calls on a new client authenticate only once."""
    transport = _RecordingTransport()
    results: list[object] = []

    async with AsyncClient(
        rpc_url,
        integration_username,
        integration_password,
        transport=transport,
    ) as new_client:

        async def fetch() -> None:
            results.append(await new_client.list_questions(survey_id))

        async with anyio.create_task_group() as tg:
            for _ in range(8):
                tg.start_soon(fetch)

    assert len(results) == 8
    assert results.count(results[0]) == 8
    assert transport.rpc_methods.count("get_session_key") == 1
    # The key is released on exit
    assert transport.rpc_methods[-1] == "release_session_key"

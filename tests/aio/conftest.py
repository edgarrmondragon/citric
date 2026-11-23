# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Fixtures for the async API tests."""

from __future__ import annotations

import json
import time
from typing import TYPE_CHECKING, Any

import pytest
from werkzeug.wrappers import Response

if TYPE_CHECKING:
    from collections.abc import Callable

    from pytest_httpserver import HTTPServer
    from werkzeug.wrappers import Request

SESSION_KEY = "async-session-key"


class RPCServer:
    """A minimal LSRC2 responder that records the calls it receives."""

    def __init__(self, httpserver: HTTPServer) -> None:
        self.calls: list[tuple[str, list[Any]]] = []
        self.auth_delay = 0.0
        self.overrides: dict[str, Callable[[int], Response]] = {}
        self.results: dict[str, Any] = {}
        httpserver.expect_request("/", method="POST").respond_with_handler(self.handle)
        self.url = httpserver.url_for("/")

    def handle(self, request: Request) -> Response:
        """Serve one RPC request."""
        payload = request.json
        method, params, request_id = payload["method"], payload["params"], payload["id"]
        self.calls.append((method, params))

        if method in self.overrides:
            return self.overrides[method](request_id)

        if method == "get_session_key":
            time.sleep(self.auth_delay)
            result: Any = SESSION_KEY
        else:
            result = self.results.get(method, "OK")

        return self.reply(request_id, result)

    @staticmethod
    def reply(
        request_id: int,
        result: Any = None,  # ruff: ignore[any-type]
        error: Any = None,  # ruff: ignore[any-type]
    ) -> Response:
        """Build a JSON-RPC response."""
        return Response(
            json.dumps({"id": request_id, "result": result, "error": error}),
            content_type="application/json",
        )

    def methods(self) -> list[str]:
        """Names of the methods called so far."""
        return [method for method, _ in self.calls]


@pytest.fixture
def server(httpserver: HTTPServer) -> RPCServer:
    """A recording RPC server."""
    return RPCServer(httpserver)

# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Unit tests exercising `HTTPTransport` with alternate HTTP client libraries.

These tests run a real request over the network (to a local
:mod:`pytest_httpserver` instance) with both :py:class:`requests.Session
<requests.Session>` and :py:class:`httpx2.Client <httpx2.Client>`, to make
sure ``Session``/``Client`` aren't secretly relying on ``requests``-only
behavior.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest
import requests
from werkzeug.wrappers import Response

from citric.client import Client
from citric.session import Session
from citric.transport.httpx2 import Httpx2Transport
from citric.transport.protocol import HTTPTransport
from citric.transport.stdlib import StdlibTransport
from citric.transport.urllib3 import Urllib3Transport

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import TypeAlias

    from pytest_httpserver import HTTPServer
    from werkzeug.wrappers import Request

    TransportFactory: TypeAlias = Callable[[], HTTPTransport]

SESSION_KEY = "session-key-from-httpserver"

transport_factories = pytest.mark.parametrize(
    "transport_factory",
    [
        pytest.param(requests.Session, id="requests"),
        pytest.param(Httpx2Transport, id="httpx2"),
        pytest.param(StdlibTransport, id="stdlib"),
        pytest.param(Urllib3Transport, id="urllib3"),
    ],
)


def rpc_handler(request: Request) -> Response:
    """Serve a minimal LSRC2 responder backed by a real HTTP server."""
    payload = request.json
    method = payload["method"]
    request_id = payload["id"]

    result = SESSION_KEY if method == "get_session_key" else "OK"

    return Response(
        json.dumps({"id": request_id, "result": result, "error": None}),
        content_type="application/json",
    )


@transport_factories
def test_transport_satisfies_protocol(transport_factory: TransportFactory):
    """Both requests.Session and httpx2.Client satisfy HTTPTransport at runtime."""
    assert isinstance(transport_factory(), HTTPTransport)


@transport_factories
def test_session_over_http_transport(
    httpserver: HTTPServer,
    transport_factory: TransportFactory,
):
    """A Session drives a full login/RPC/close cycle over any HTTPTransport."""
    httpserver.expect_request("/", method="POST").respond_with_handler(rpc_handler)

    transport = transport_factory()

    with Session(
        httpserver.url_for("/"),
        "user",
        "password",
        requests_session=transport,
    ) as session:
        assert session.key == SESSION_KEY
        assert session.__ok() == "OK"

    assert session.closed


@transport_factories
def test_client_over_http_transport(
    httpserver: HTTPServer,
    transport_factory: TransportFactory,
):
    """A Client works the same way regardless of the underlying HTTPTransport."""
    httpserver.expect_request("/", method="POST").respond_with_handler(rpc_handler)

    transport = transport_factory()

    with Client(
        httpserver.url_for("/"),
        "user",
        "password",
        requests_session=transport,
    ) as client:
        assert client.session.key == SESSION_KEY

    assert client.session.closed

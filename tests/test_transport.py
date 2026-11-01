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
import re
from contextlib import nullcontext
from typing import TYPE_CHECKING

import httpcore2
import httpx2
import pytest
import requests
from werkzeug.wrappers import Response

from citric.client import Client
from citric.rest import RESTClient
from citric.session import Session
from citric.transport.httpx2 import Httpx2Transport
from citric.transport.protocol import HTTPTransport
from citric.transport.urllib3 import Urllib3Transport
from tests.fixtures import requests_session_warning

if TYPE_CHECKING:
    from collections.abc import Callable
    from contextlib import AbstractContextManager
    from typing import TypeAlias

    from pytest_httpserver import HTTPServer
    from werkzeug.wrappers import Request

    TransportFactory: TypeAlias = Callable[[], HTTPTransport]

SESSION_KEY = "session-key-from-httpserver"
REST_SESSION_ID = "my-api-token"

transport_factories = pytest.mark.parametrize(
    "transport_factory",
    [
        pytest.param(requests.Session, id="requests"),
        pytest.param(Httpx2Transport, id="httpx2"),
        pytest.param(Urllib3Transport, id="urllib3"),
    ],
)

transport_parameters = pytest.mark.parametrize(
    ("parameter", "effect"),
    [
        pytest.param(
            "requests_session",
            requests_session_warning,
            id="requests_session",
        ),
        pytest.param("transport", nullcontext(), id="transport"),
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


def rest_handler(request: Request) -> Response:
    """Serve a minimal REST responder backed by a real HTTP server."""
    if request.method == "POST" and request.path == "/rest/v1/auth":
        return Response(
            json.dumps({"token": REST_SESSION_ID}),
            content_type="application/json",
        )

    return Response('{"survey": {"foo": "bar"}}', content_type="application/json")


@transport_factories
def test_transport_satisfies_protocol(transport_factory: TransportFactory):
    """Both requests.Session and httpx2.Client satisfy HTTPTransport at runtime."""
    assert isinstance(transport_factory(), HTTPTransport)


@transport_factories
def test_transport_bytes(httpserver: HTTPServer, transport_factory: TransportFactory):
    """Test that the transport can handle bytes data."""
    path = re.compile(r"^/path/to/endpoint")
    httpserver.expect_request(path).respond_with_json({"status": "ok"})

    transport = transport_factory()
    response = transport.request(
        "POST",
        httpserver.url_for("/path/to/endpoint"),
        data=b'{"username": "user", "password": "password"}',
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@transport_factories
@transport_parameters
def test_session_over_http_transport(
    httpserver: HTTPServer,
    transport_factory: TransportFactory,
    parameter: str,
    effect: AbstractContextManager,
):
    """A Session drives a full login/RPC/close cycle over any HTTPTransport."""
    httpserver.expect_request("/", method="POST").respond_with_handler(rpc_handler)

    transport = transport_factory()

    with (
        effect,
        Session(
            httpserver.url_for("/"),
            "user",
            "password",
            **{parameter: transport},  # type: ignore[arg-type] # ty: ignore[invalid-argument-type]
        ) as session,
    ):
        assert session.key == SESSION_KEY
        assert session.__ok() == "OK"

    assert session.closed
    assert session._transport is transport


@transport_factories
@transport_parameters
def test_client_over_http_transport(
    httpserver: HTTPServer,
    transport_factory: TransportFactory,
    parameter: str,
    effect: AbstractContextManager,
):
    """A Client works the same way regardless of the underlying HTTPTransport."""
    httpserver.expect_request("/", method="POST").respond_with_handler(rpc_handler)

    transport = transport_factory()

    with (
        effect,
        Client(
            httpserver.url_for("/"),
            "user",
            "password",
            **{parameter: transport},  # type: ignore[arg-type] # ty: ignore[invalid-argument-type]
        ) as client,
    ):
        assert client.session.key == SESSION_KEY

    assert client.session.closed
    assert client.session._transport is transport


@transport_factories
@transport_parameters
def test_rest_client_over_http_transport(
    httpserver: HTTPServer,
    transport_factory: TransportFactory,
    parameter: str,
    effect: AbstractContextManager,
):
    """A REST client works the same way regardless of the underlying HTTPTransport."""
    httpserver.expect_request(re.compile(r"^/rest/v1")).respond_with_handler(
        rest_handler
    )

    transport = transport_factory()

    with (
        effect,
        RESTClient(
            httpserver.url_for("/").rstrip("/"),
            "user",
            "password",
            **{parameter: transport},
        ) as client,
    ):
        assert client.session_id == REST_SESSION_ID
        assert client.get_survey_details(1) == {"foo": "bar"}

    assert client._transport is transport


client_classes = pytest.mark.parametrize(
    "client_class",
    [
        pytest.param(Session, id="Session"),
        pytest.param(Client, id="Client"),
        pytest.param(RESTClient, id="RESTClient"),
    ],
)


@client_classes
def test_both_transport_requests_session_error(
    client_class: type[Session | Client | RESTClient],
):
    """Test setting both 'transport' and 'requests_session' raises a TypeError."""
    with pytest.raises(
        TypeError,
        match="Both 'transport' and 'requests_session' are set",
    ):
        _ = client_class(
            "https://example.com",
            "user",
            "password",
            transport=Urllib3Transport(),
            requests_session=requests.Session(),
        )


@client_classes
def test_requests_session_warning_location(
    httpserver: HTTPServer,
    client_class: type[Session | Client | RESTClient],
):
    """The deprecation warning is attributed to the caller, not citric internals.

    Python only shows a ``DeprecationWarning`` by default when it points at user code.
    """
    httpserver.expect_request("/", method="POST").respond_with_handler(rpc_handler)
    httpserver.expect_request(re.compile(r"^/rest/v1")).respond_with_handler(
        rest_handler
    )

    with pytest.warns(
        DeprecationWarning,
        match="Parameter 'requests_session' is deprecated",
    ) as record:
        instance = client_class(
            httpserver.url_for("/"),
            "user",
            "password",
            requests_session=requests.Session(),
        )

    instance.close()
    assert [w.filename for w in record] == [__file__]


def test_urllib3_transport_pool_options():
    """Pool options are passed to the underlying `PoolManager`."""
    transport = Urllib3Transport(num_pools=3, maxsize=16, block=True, timeout=7)
    pool = transport._pool
    assert pool.pools._maxsize == 3
    assert pool.connection_pool_kw["maxsize"] == 16
    assert pool.connection_pool_kw["block"] is True
    assert pool.connection_pool_kw["timeout"] == 7
    transport.close()


def test_httpx2_transport_pool_options():
    """Pool options are passed to the underlying `httpx2.Client`."""
    transport = Httpx2Transport(
        max_connections=32,
        max_keepalive_connections=16,
        keepalive_expiry=30,
    )

    inner_transport = transport._client._transport
    assert isinstance(inner_transport, httpx2.HTTPTransport)

    pool = inner_transport._pool
    assert isinstance(pool, httpcore2.ConnectionPool)
    assert pool._max_connections == 32
    assert pool._max_keepalive_connections == 16
    assert pool._keepalive_expiry == 30
    transport.close()

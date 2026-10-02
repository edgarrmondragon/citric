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
from typing import TYPE_CHECKING, Any

import pytest
import requests
from werkzeug.wrappers import Response

from citric.client import Client
from citric.rest import RESTClient
from citric.session import Session
from citric.transport.httpx2 import Httpx2Transport
from citric.transport.protocol import HTTPTransport
from citric.transport.urllib3 import Urllib3Transport

if TYPE_CHECKING:
    from collections.abc import Callable
    from contextlib import AbstractContextManager
    from typing import TypeAlias

    from pytest_httpserver import HTTPServer
    from werkzeug.wrappers import Request

    TransportFactory: TypeAlias = Callable[[], HTTPTransport]

SESSION_KEY = "session-key-from-httpserver"
REST_SESSION_ID = "my-api-token"

requests_session_warning = pytest.warns(
    DeprecationWarning,
    match="Parameter 'requests_session' is deprecated",
)

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
            httpserver.url_for("/"),
            "user",
            "password",
            **{parameter: transport},
        ) as client,
    ):
        assert client.session_id == REST_SESSION_ID
        assert client.get_survey_details(1) == {"foo": "bar"}


def test_client_custom_session_kwargs(httpserver: HTTPServer):
    """A Client can be instantiated with a custom session."""
    httpserver.expect_request("/", method="POST").respond_with_handler(rpc_handler)

    class CustomSession(Session):
        def __init__(
            self,
            url: str,
            username: str,
            password: str,
            requests_session: HTTPTransport,
            **kwargs: Any,
        ):
            super().__init__(
                url,
                username,
                password,
                requests_session=requests_session,  # type: ignore[call-arg] # ty: ignore[unknown-argument]
                **kwargs,
            )

    class CustomClient(Client):
        session_class = CustomSession  # type: ignore[assignment]

    with (
        requests_session_warning,
        CustomClient(
            httpserver.url_for("/"),
            "user",
            "password",
            transport=Urllib3Transport(),
        ) as client,
    ):
        assert client.session.key == SESSION_KEY

    class TransportSession(Session):
        def __init__(
            self,
            url: str,
            username: str,
            password: str,
            transport: HTTPTransport,
            **kwargs: Any,
        ):
            super().__init__(
                url,
                username,
                password,
                transport=transport,
                **kwargs,
            )

    class TransportClient(Client):
        session_class = TransportSession  # type: ignore[assignment]

    with (
        requests_session_warning,
        CustomClient(
            httpserver.url_for("/"),
            "user",
            "password",
            transport=Urllib3Transport(),
        ) as client,
    ):
        assert client.session.key == SESSION_KEY

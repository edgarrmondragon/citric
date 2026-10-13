# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Unit tests for the Python Client."""

from __future__ import annotations

import datetime as dt
import json
import sys
import warnings
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import pytest

from citric.client import Client, ServerVersion
from citric.session import Session

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:
    from collections.abc import Generator


DUMMY_FILE_CONTENTS = b"FILE CONTENTS"


@dataclass
class _Response:
    status_code: int
    data: Any

    def json(self) -> Any:  # ruff: ignore[any-type]
        return self.data


class _Transport:
    def request(self, *args: Any, data: str | None = None, **kwargs: Any) -> _Response:
        payload = json.loads(data)  # type: ignore[arg-type] # ty: ignore[invalid-argument-type]
        if payload["method"] == "export_timeline":
            result: dict[str, Any] = {"2022-01-01": 4, "2022-01-02": 2}
        else:
            result = {"method": payload["method"], "params": payload["params"]}

        return _Response(200, {"id": payload["id"], "result": result, "error": None})

    def close(self) -> None: ...


@pytest.fixture(scope="session")
def client() -> Generator[Client, None, None]:
    """RemoteControl2 API client."""
    with pytest.warns(
        DeprecationWarning,
        match="Parameter 'requests_session' is deprecated; use 'transport' instead",
    ):
        client = Client("mock://lime.com", "u", "p", requests_session=_Transport())

    try:
        yield client
    finally:
        client.close()


def test_session_class_deprecation():
    """The ``session_class`` warning is attributed to the caller, not citric."""

    class MockSession(Session): ...

    class MockClient(Client):
        session_class = MockSession

    with pytest.warns(
        DeprecationWarning,
        match="Using a custom class in `Client.session_class` is deprecated",
    ) as record:
        client = MockClient(
            "mock://lime.com",
            "u",
            "p",
            transport=_Transport(),
            connect=True,
        )

    assert isinstance(client.session, MockSession)
    client.close()

    assert [w.filename for w in record] == [__file__]


def test_export_timeline(client: Client):
    """Test export_timeline client method."""
    assert client.export_timeline(
        1,
        "hour",
        dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc),
    ) == {
        "2022-01-01": 4,
        "2022-01-02": 2,
    }


def test_invite_participants_unknown_status(client: Client):
    """Test invite_participants client method."""
    with pytest.raises(RuntimeError, match="Could not determine invitation status"):
        client.invite_participants(1)


@pytest.mark.parametrize(
    ("raw", "parsed"),
    [
        ("6.1.0", ServerVersion(6, 1)),
        ("6.5.0-dev", ServerVersion(6, 5, prerelease="dev")),
        ("7.0.0-beta1", ServerVersion(7, prerelease="beta1")),
        ("7.0.0-RC1", ServerVersion(7, prerelease="rc1")),
        ("NOMATCH", ServerVersion._default()),
    ],
)
def test_parse_server_version(raw: str, parsed: tuple):
    """Test server version parsing."""
    assert ServerVersion.parse(raw) == parsed


def test_session_class_requests_session_only():
    """A custom ``session_class`` that only accepts ``requests_session`` still works."""
    transport = _Transport()

    class LegacySession(Session):
        def __init__(
            self,
            url: str,
            username: str,
            password: str,
            *,
            requests_session: _Transport,
            auth_plugin: str,
        ) -> None:
            super().__init__(
                url,
                username,
                password,
                transport=requests_session,
                auth_plugin=auth_plugin,
            )

    class LegacyClient(Client):
        session_class = LegacySession

    with pytest.warns(DeprecationWarning, match="`Client.session_class` is deprecated"):
        client = LegacyClient("mock://lime.com", "u", "p", transport=transport)

    assert client.session._transport is transport
    client.close()


class _RecordingTransport(_Transport):
    def __init__(self) -> None:
        self.methods: list[str] = []

    @override
    def request(self, *args: Any, data: str | None = None, **kwargs: Any) -> _Response:
        self.methods.append(json.loads(data)["method"])  # type: ignore[arg-type] # ty: ignore[invalid-argument-type]
        return super().request(*args, data=data, **kwargs)


def test_lazy_connect():
    """With ``connect=False`` no request is made until the key is needed."""
    transport = _RecordingTransport()
    client = Client("mock://lime.com", "u", "p", transport=transport, connect=False)
    assert transport.methods == []

    assert client.session.key is not None
    assert transport.methods == ["get_session_key"]

    client.close()
    assert transport.methods == ["get_session_key", "release_session_key"]
    assert client.session.closed


def test_close_without_connecting():
    """Closing a never-connected session doesn't hit the server."""
    transport = _RecordingTransport()
    Client("mock://lime.com", "u", "p", transport=transport, connect=False).close()
    assert transport.methods == []


@pytest.mark.parametrize("client_class", [Session, Client])
def test_connect_future_warning(client_class: type[Session | Client]):
    """Omitting ``connect`` warns, attributed to the caller; passing it doesn't."""
    with pytest.warns(FutureWarning, match="default value of `connect`") as record:
        instance = client_class("mock://lime.com", "u", "p", transport=_Transport())

    assert [w.filename for w in record] == [__file__]
    instance.close()

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        client_class(
            "mock://lime.com", "u", "p", transport=_Transport(), connect=True
        ).close()


def test_session_class_without_connect_parameter():
    """A custom ``session_class`` that doesn't accept ``connect`` still works."""

    class NoConnectSession(Session):
        def __init__(
            self,
            url: str,
            username: str,
            password: str,
            *,
            transport: _Transport,
            auth_plugin: str,
        ) -> None:
            super().__init__(
                url,
                username,
                password,
                transport=transport,
                auth_plugin=auth_plugin,
                connect=True,
            )

    class NoConnectClient(Client):
        session_class = NoConnectSession

    transport = _Transport()
    with pytest.warns(DeprecationWarning, match="`Client.session_class` is deprecated"):
        client = NoConnectClient("mock://lime.com", "u", "p", transport=transport)

    assert isinstance(client.session, NoConnectSession)
    client.close()

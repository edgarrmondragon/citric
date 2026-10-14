# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Unit tests for the Python Client."""

from __future__ import annotations

import datetime as dt
import json
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import pytest

from citric.client import Client, ServerVersion
from citric.exceptions import LimeSurveyApiError
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


def test_transport_is_closed_if_release_fails():
    """The transport is closed even if releasing the session key fails."""

    class FailingReleaseTransport(_Transport):
        closed = 0

        @override
        def request(
            self, *args: Any, data: str | None = None, **kwargs: Any
        ) -> _Response:
            if json.loads(data)["method"] == "release_session_key":  # type: ignore[arg-type] # ty: ignore[invalid-argument-type]
                return _Response(500, None)
            return super().request(*args, data=data, **kwargs)

        @override
        def close(self) -> None:
            self.closed += 1

    transport = FailingReleaseTransport()
    session = Session("mock://lime.com", "u", "p", transport=transport)

    with pytest.raises(LimeSurveyApiError):
        session.close()

    assert transport.closed == 1
    assert session.closed


def test_close_is_idempotent():
    """Closing a session again doesn't hit the server or the transport."""

    class RecordingTransport(_Transport):
        def __init__(self) -> None:
            self.methods: list[str] = []
            self.closed = 0

        @override
        def request(
            self, *args: Any, data: str | None = None, **kwargs: Any
        ) -> _Response:
            self.methods.append(json.loads(data)["method"])  # type: ignore[arg-type] # ty: ignore[invalid-argument-type]
            return super().request(*args, data=data, **kwargs)

        @override
        def close(self) -> None:
            self.closed += 1

    transport = RecordingTransport()
    session = Session("mock://lime.com", "u", "p", transport=transport)

    session.close()
    session.close()

    assert transport.methods == ["get_session_key", "release_session_key"]
    assert transport.closed == 1


def test_session_is_closed_if_transport_close_fails():
    """The session state is updated even if the transport fails to close."""

    class FailingCloseTransport(_Transport):
        @override
        def close(self) -> None:
            msg = "boom"
            raise RuntimeError(msg)

    session = Session("mock://lime.com", "u", "p", transport=FailingCloseTransport())

    with pytest.raises(RuntimeError, match="boom"):
        session.close()

    assert session.closed
    assert session.key is None

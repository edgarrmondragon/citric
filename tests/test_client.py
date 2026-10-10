# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Unit tests for the Python Client."""

from __future__ import annotations

import datetime
import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import pytest

from citric.client import Client, ServerVersion

if TYPE_CHECKING:
    from collections.abc import Generator


DUMMY_FILE_CONTENTS = b"FILE CONTENTS"


@dataclass
class _Response:
    status_code: int
    data: Any

    @property
    def content(self) -> bytes:
        return json.dumps(self.data).encode()

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
    with Client("mock://lime.com", "u", "p", requests_session=_Transport()) as client:
        yield client


def test_export_timeline(client: Client):
    """Test export_timeline client method."""
    assert client.export_timeline(
        1,
        "hour",
        datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc),
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

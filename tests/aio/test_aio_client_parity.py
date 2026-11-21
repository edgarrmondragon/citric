# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Check that the async client mirrors the sync one."""

from __future__ import annotations

import inspect

import pytest

from citric.aio.client import AsyncClient
from citric.client import Client

#: Sync-only API, and its async replacement, if any.
RENAMED = {"close": "aclose"}


def _public_methods(cls: type) -> dict[str, object]:
    return {
        name: member
        for name, member in inspect.getmembers(cls, inspect.isfunction)
        if not name.startswith("_")
    }


def _parameters(func: object) -> list[tuple[str, object, object]]:
    return [
        (p.name, p.kind, p.default)
        for p in inspect.signature(func).parameters.values()  # type: ignore[arg-type] # ty: ignore[invalid-argument-type]
    ]


@pytest.mark.parametrize("name", sorted(_public_methods(Client)))
def test_async_client_mirrors_sync_method(name: str):
    """Every public method of Client has an async counterpart with the same params."""
    sync = _public_methods(Client)[name]
    async_name = RENAMED.get(name, name)

    assert hasattr(AsyncClient, async_name), f"{async_name} is missing"
    counterpart = getattr(AsyncClient, async_name)

    assert inspect.iscoroutinefunction(counterpart) or inspect.isasyncgenfunction(
        counterpart,
    )
    assert _parameters(counterpart) == _parameters(sync)
    assert counterpart.__doc__


def test_async_client_has_no_extra_public_methods():
    """The async client doesn't grow methods that the sync client lacks."""
    sync_names = {RENAMED.get(name, name) for name in _public_methods(Client)}
    extra = set(_public_methods(AsyncClient)) - sync_names
    assert not extra

# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Run the async client through the synchronous integration tests.

:class:`BlockingProxy` wraps an :class:`~citric.aio.client.AsyncClient` so that it can
stand in for a :class:`citric.Client`: each method call runs the coroutine in a
background event loop and blocks until it's done. One set of tests then covers both
clients.
"""

from __future__ import annotations

import contextlib
import functools
import inspect
from typing import TYPE_CHECKING, Any, cast
from unittest.mock import AsyncMock, patch

from anyio.from_thread import start_blocking_portal

from citric.aio.client import AsyncClient
from citric.aio.session import AsyncSession

if TYPE_CHECKING:
    from collections.abc import Callable, Generator

    from anyio.from_thread import BlockingPortal

    import citric


class BlockingProxy:
    """Expose the async methods of an object as blocking calls.

    Coroutines are awaited, async generators are collected into an iterator, and
    :class:`~citric.aio.session.AsyncSession` attributes are wrapped as well. Every
    other attribute is assumed to be an async method.
    """

    def __init__(self, target: object, portal: BlockingPortal) -> None:
        self.__wrapped__ = target
        self._portal = portal

    def __getattr__(self, name: str) -> Any:  # ruff: ignore[any-type]
        """Get an attribute of the wrapped object, made blocking if it's async.

        Returns:
            The attribute.
        """
        value = getattr(self.__wrapped__, name)
        if isinstance(value, AsyncSession):
            return BlockingProxy(value, self._portal)

        def call(*args: Any, **kwargs: Any) -> Any:  # ruff: ignore[any-type]
            return self._portal.call(_invoke, value, args, kwargs)

        return call


async def _invoke(
    func: Callable[..., Any],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> Any:  # ruff: ignore[any-type]
    result = func(*args, **kwargs)
    if inspect.isasyncgen(result):
        return iter([item async for item in result])
    return await result


@contextlib.contextmanager
def blocking_async_client(
    url: str,
    username: str,
    password: str,
) -> Generator[citric.Client, None, None]:
    """Create an async client that can be used like a sync one.

    Yields:
        The wrapped async client, typed as the sync client it stands in for.
    """
    with start_blocking_portal() as portal:
        # Create the client in the event loop thread, where it's used
        aclient = portal.call(functools.partial(AsyncClient, url, username, password))
        try:
            yield cast("citric.Client", BlockingProxy(aclient, portal))
        finally:
            portal.call(aclient.aclose)


@contextlib.contextmanager
def patch_client_method(
    client: object,
    name: str,
    return_value: object,
) -> Generator[None, None, None]:
    """Patch a method of a sync client, or of an async client behind a proxy.

    Args:
        client: The client to patch.
        name: Name of the method.
        return_value: The value the patched method returns.

    Yields:
        Nothing, while the method is patched.
    """
    if isinstance(client, BlockingProxy):
        with patch.object(
            client.__wrapped__,
            name,
            AsyncMock(return_value=return_value),
        ):
            yield
    else:
        with patch.object(client, name, return_value=return_value):
            yield

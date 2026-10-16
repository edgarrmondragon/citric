# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Low level async wrapper for connecting to the LSRC2."""

from __future__ import annotations

__lazy_modules__ = {
    "asyncio",
    "citric._rpc",
    "citric.method",
    "json",
}

import asyncio
import json
from typing import TYPE_CHECKING, Any, Type  # ruff: ignore[deprecated-import]

from citric import _rpc
from citric.method import Method

if TYPE_CHECKING:
    import sys
    from collections.abc import Coroutine
    from types import TracebackType

    from citric.aio.transport.protocol import AsyncHTTPTransport
    from citric.types import Result, RPCRequest, RPCResponse

    if sys.version_info >= (3, 11):
        from typing import Self
    else:
        from typing_extensions import Self

__all__ = ["AsyncSession"]


class AsyncSession:
    """Asynchronous LimeSurvey RemoteControl 2 session.

    The async counterpart of :class:`citric.session.Session`. Retrieves a session key
    with :ls_manual:`get_session_key <RemoteControl_2_API#get_session_key>` the first
    time it is needed. Creating a session doesn't contact the server. The key is
    released upon session :meth:`closure <aclose>`, if one was retrieved.

    Concurrent tasks sharing a new session authenticate only once.

    Args:
        url: LimeSurvey Remote Control endpoint.
        username: LimeSurvey user name.
        password: LimeSurvey password.
        transport: An HTTP transport implementing
            :class:`~citric.aio.transport.protocol.AsyncHTTPTransport`. Defaults to a
            new :class:`~citric.aio.transport.httpx2.AsyncHttpx2Transport`, which
            requires ``httpx2`` to be installed.
        auth_plugin: Name of the :ls_manual:`plugin <Authentication_plugins>` to use for
            authentication. Defaults to the
            :ls_manual:`internal database <Authentication_plugins#Internal_database>`
            (``"Authdb"``).
        json_encoder: A :py:class:`json.Encoder <json.JSONEncoder>` subclass to use for
            encoding RPC parameters.

    .. versionadded:: NEXT_VERSION
    """

    USER_AGENT = _rpc.USER_AGENT

    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        *,
        auth_plugin: str = "Authdb",
        transport: AsyncHTTPTransport | None = None,
        json_encoder: Type[json.JSONEncoder] | None = None,  # ruff: ignore[non-pep585-annotation]
    ) -> None:
        if transport is None:
            from citric.aio.transport.httpx2 import AsyncHttpx2Transport  # ruff: ignore[import-outside-top-level]

            transport = AsyncHttpx2Transport()

        self.url: str = url
        self._transport = transport
        self._encoder = json_encoder or json.JSONEncoder
        self.__lock = asyncio.Lock()
        self.__closed: bool = False
        self.__key: str | None = None
        self.__credentials: tuple[str, str, str] | None = (
            username,
            password,
            auth_plugin,
        )

    @property
    def closed(self) -> bool:
        """Whether the RPC session is closed."""
        return self.__closed

    async def get_key(self) -> str | None:
        """Get the RPC session key.

        The first call authenticates with the server.

        Returns:
            The session key.
        """
        async with self.__lock:
            if self.__credentials is not None:
                username, password, auth_plugin = self.__credentials
                self.__key = await self.rpc(
                    _rpc.GET_SESSION_KEY,
                    username,
                    password,
                    auth_plugin,
                )
                self.__credentials = None
            return self.__key

    def __getattr__(self, name: str) -> Method[Coroutine[Any, Any, Result]]:
        """Magic method dispatcher.

        Args:
            name: Name of the method to call.

        Returns:
            A method object, to be called and awaited.
        """
        return Method(self.rpc, name)

    async def call(self, method: str, *params: Any) -> RPCResponse:
        """Get the raw response from an RPC method.

        Args:
            method: Name of the method to call.
            params: Positional arguments of the RPC method.

        Returns:
            An RPC result.
        """
        if not _rpc.needs_session_key(method):
            return await self._invoke(method, *params)

        # Methods requiring authentication
        return await self._invoke(method, await self.get_key(), *params)

    async def rpc(self, method: str, *params: Any) -> Result:
        """Execute a LimeSurvey RPC call with error handling.

        Args:
            method: Name of the method to call.
            params: Positional arguments of the RPC method.

        Returns:
            An RPC result.
        """
        response = await self.call(method, *params)
        _rpc.check_result_status(response["result"])
        return response["result"]

    async def _invoke(self, method: str, *params: Any) -> RPCResponse:
        payload: RPCRequest = _rpc.new_request(method, params)
        res = await self._transport.request(
            "POST",
            self.url,
            data=_rpc.encode_request(payload, self._encoder),
            headers=_rpc.request_headers(),
        )
        return _rpc.parse_response(res, payload)

    async def aclose(self) -> None:
        """Close RPC session.

        Releases the session key with
        :ls_manual:`release_session_key <RemoteControl_2_API#release_session_key>`.

        Closing a session more than once has no effect. The session is closed, and its
        HTTP transport released, even if releasing the session key fails.
        """
        # Wait for an in-flight deferred connection so its key gets released
        async with self.__lock:
            if self.__closed:
                return

            try:
                if self.__key is not None:
                    response = await self._invoke("release_session_key", self.__key)
                    _rpc.check_result_status(response["result"])
            finally:
                # Update the state first, so it's consistent if the transport fails
                self.__key = None
                self.__credentials = None
                self.__closed = True
                await self._transport.aclose()

    async def __aenter__(self: Self) -> Self:
        """Context manager for RPC session.

        Returns:
            LimeSurvey RPC session.
        """
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException] | None,  # ruff: ignore[non-pep585-annotation]
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Safely exit an RPC session.

        Args:
            exc_type: Exception class.
            exc_value: Exception instance.
            traceback: Error traceback.
        """
        await self.aclose()

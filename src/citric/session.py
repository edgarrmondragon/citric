# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Low level wrapper for connecting to the LSRC2."""

from __future__ import annotations

__lazy_modules__ = {
    "citric.exceptions",
    "citric.method",
    "importlib",
    "json",
    "random",
    "httpx2",
}

import json
import logging
import random
from importlib import metadata
from typing import TYPE_CHECKING, Any, Sequence, Type, TypedDict  # ruff: ignore[deprecated-import]

import httpx2
from deprecated.params import deprecated_params

from citric.exceptions import (
    InvalidJSONResponseError,
    LimeSurveyApiError,
    LimeSurveyStatusError,
    ResponseMismatchError,
    RPCInterfaceNotEnabledError,
)
from citric.method import AsyncMethod, Method

if TYPE_CHECKING:
    import sys
    from types import TracebackType

    import requests

    from citric.types import Result, RPCResponse

    if sys.version_info >= (3, 11):
        from typing import Self
    else:
        from typing_extensions import Self

__all__ = ["Session"]

GET_SESSION_KEY = "get_session_key"

logger: logging.Logger = logging.getLogger(__name__)


def handle_rpc_errors(result: Result, error: str | None) -> None:
    """Handle RPC errors.

    Args:
        result: The result of the RPC call.
        error: The error message of the RPC call.

    Raises:
        LimeSurveyStatusError: The response key from the response payload has
            a non-null status.
        LimeSurveyApiError: The response payload has a non-null error key.
    """
    if error is not None:
        raise LimeSurveyApiError(error)

    if not isinstance(result, dict):
        return

    if result.get("status") not in {"OK", None}:
        raise LimeSurveyStatusError(
            result["status"],
            error_code=result.get("error_code"),
        )


class Payload(TypedDict):
    method: str
    params: Sequence[Any]
    id: int


def prepare_request_payload(method: str, *params: Any) -> Payload:
    request_id = random.randint(1, 999_999)  # ruff: ignore[suspicious-non-cryptographic-random-usage]

    return {
        "method": method,
        "params": [*params],
        "id": request_id,
    }


def handle_response(payload: Payload, res: httpx2.Response) -> RPCResponse:
    res.raise_for_status()

    if not res.text:
        raise RPCInterfaceNotEnabledError

    data: RPCResponse

    try:
        data = res.json()
    except json.JSONDecodeError as e:
        raise InvalidJSONResponseError from e

    request_id = payload["id"]

    logger.info("Invoked RPC method %s with ID %d", payload["method"], request_id)

    if (response_id := data["id"]) != request_id:
        msg = f"Response ID {response_id} does not match request ID {request_id}"
        raise ResponseMismatchError(msg)

    return data


class BaseSession:
    USER_AGENT = f"citric/{metadata.version('citric')}"

    def __init__(self, url: str) -> None:
        self.url: str = url

        self.__key: str | None = None

        self.__closed = False

    @property
    def closed(self) -> bool:
        """Whether the RPC session is closed."""
        return self.__closed

    @property
    def key(self) -> str | None:
        """RPC session key."""
        return self.__key

    def _close(self) -> None:
        """Close RPC session.

        Releases the session key with
        :ls_manual:`release_session_key <RemoteControl_2_API#release_session_key>`.
        """
        self.__key = None
        self.__closed = True


class Session(BaseSession):
    """LimeSurvey RemoteControl 2 session.

    Upon creation, retrieves a session key with
    :ls_manual:`get_session_key <RemoteControl_2_API#get_session_key>` and stores it in
    the `key`_ attribute. The key is released upon session `closure`_.

    Args:
        url: LimeSurvey Remote Control endpoint.
        username: LimeSurvey user name.
        password: LimeSurvey password.
        httpx_client: A :py:class:`httpx2.Client <httpx2.Client>` object.
        requests_session: [DEPRECATED] A :py:class:`requests.Session <requests.Session>`
            object.
        auth_plugin: Name of the :ls_manual:`plugin <Authentication_plugins>` to use for
            authentication. For example,
            :ls_manual:`AuthLDAP <Authentication_plugins#LDAP>`. Defaults to using the
            :ls_manual:`internal database <Authentication_plugins#Internal_database>`
            (``"Authdb"``).
        json_encoder: [DEPRECATED] A :py:class:`json.Encoder <json.JSONEncoder>`
            subclass to use for encoding RPC parameters.

    .. versionchanged:: 0.0.4
       Replaced the ``requests_session_factory`` parameter with ``requests_session``.

    .. versionadded:: 0.0.6
       Support Auth plugins with the ``auth_plugin`` parameter.

    .. versionadded:: 0.5.0
       The ``json_encoder`` parameter.


    .. _key: #citric.session.Session.key
    .. _closure: #citric.session.Session.close
    """

    @deprecated_params(
        "requests_session",
        reason="requests_session is no longer used since version v3.0.0. Use httpx_client instead",  # ruff: ignore[line-too-long]
    )
    @deprecated_params(
        "json_encoder", reason="json_encoder is no longer used since version v3.0.0"
    )
    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        *,
        auth_plugin: str = "Authdb",
        httpx_client: httpx2.Client | None = None,
        requests_session: requests.Session | None = None,  # ruff: ignore[unused-method-argument]
        json_encoder: Type[json.JSONEncoder] | None = None,  # ruff: ignore[non-pep585-annotation, unused-method-argument]
    ) -> None:
        super().__init__(url)
        self._client = httpx_client or httpx2.Client()
        self._client.headers["User-Agent"] = self.USER_AGENT

        self.__key: str | None = self.get_session_key(
            username,
            password,
            auth_plugin,
        )

    def __getattr__(self, name: str) -> Method[Result]:
        """Magic method dispatcher.

        Args:
            name: Name of the method to call.

        Returns:
            A method object.
        """
        return Method(self.rpc, name)

    def call(self, method: str, *params: Any) -> RPCResponse:
        """Get the raw response from an RPC method.

        Args:
            method: Name of the method to call.
            params: Positional arguments of the RPC method.

        Returns:
            An RPC result.
        """
        if method == GET_SESSION_KEY or method.startswith("system."):
            return self._invoke(method, *params)

        # Methods requiring authentication
        return self._invoke(method, self.key, *params)

    def rpc(self, method: str, *params: Any) -> Result:
        """Execute a LimeSurvey RPC call with error handling.

        Args:
            method: Name of the method to call.
            params: Positional arguments of the RPC method.

        Returns:
            An RPC result.
        """
        response = self.call(method, *params)
        handle_rpc_errors(response["result"], response["error"])
        return response["result"]

    def _invoke(self, method: str, *params: Any) -> RPCResponse:
        """Execute a LimeSurvey RPC with a JSON payload.

        Args:
            method: Name of the method to call.
            params: Positional arguments of the RPC method.

        Returns:
            An RPC result.

        Raises:
            ResponseMismatchError: Request ID does not match the response ID.
            RPCInterfaceNotEnabledError: If the JSON RPC interface is not enabled
                (empty response).
            InvalidJSONResponseError: If the response is not valid JSON.
        """  # ruff: ignore[docstring-extraneous-exception]
        payload = prepare_request_payload(method, *params)

        res = self._client.post(
            self.url,
            data=payload,
            headers={
                "content-type": "application/json",
            },
        )

        return handle_response(payload, res)

    def close(self) -> None:
        """Close RPC session.

        Releases the session key with
        :ls_manual:`release_session_key <RemoteControl_2_API#release_session_key>`.
        """
        self.release_session_key()
        self._client.close()
        super()._close()

    def __enter__(self: Self) -> Self:
        """Context manager for RPC session.

        Returns:
            LimeSurvey RPC session.
        """
        return self

    def __exit__(
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
        self.close()


class AsyncSession(BaseSession):
    """LimeSurvey RemoteControl 2 asynchronous session.

    Upon creation, retrieves a session key with
    :ls_manual:`get_session_key <RemoteControl_2_API#get_session_key>` and stores it in
    the `key`_ attribute. The key is released upon session `closure`_.

    Args:
        url: LimeSurvey Remote Control endpoint.
        username: LimeSurvey user name.
        password: LimeSurvey password.
        httpx_client: A :py:class:`httpx2.AsyncClient <httpx2.AsyncClient>` object.
        requests_session: [DEPRECATED] A :py:class:`requests.Session <requests.Session>`
            object.
        auth_plugin: Name of the :ls_manual:`plugin <Authentication_plugins>` to use for
            authentication. For example,
            :ls_manual:`AuthLDAP <Authentication_plugins#LDAP>`. Defaults to using the
            :ls_manual:`internal database <Authentication_plugins#Internal_database>`
            (``"Authdb"``).
        json_encoder: [DEPRECATED] A :py:class:`json.Encoder <json.JSONEncoder>`
            subclass to use for encoding RPC parameters.

    .. versionchanged:: 0.0.4
       Replaced the ``requests_session_factory`` parameter with ``requests_session``.

    .. versionadded:: 0.0.6
       Support Auth plugins with the ``auth_plugin`` parameter.

    .. versionadded:: 0.5.0
       The ``json_encoder`` parameter.


    .. _key: #citric.session.Session.key
    .. _closure: #citric.session.Session.close
    """

    @deprecated_params(
        "requests_session",
        reason="requests_session is no longer used since version v3.0.0. Use httpx_client instead",  # ruff: ignore[line-too-long]
    )
    @deprecated_params(
        "json_encoder", reason="json_encoder is no longer used since version v3.0.0"
    )
    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        *,
        auth_plugin: str = "Authdb",
        httpx_client: httpx2.AsyncClient | None = None,
        requests_session: requests.Session | None = None,  # ruff: ignore[unused-method-argument]
        json_encoder: Type[json.JSONEncoder] | None = None,  # ruff: ignore[non-pep585-annotation, unused-method-argument]
    ) -> None:
        super().__init__(url)
        self._username = username
        self._password = password
        self._auth_plugin = auth_plugin
        self._client = httpx_client or httpx2.AsyncClient()
        self._client.headers["User-Agent"] = self.USER_AGENT

    def __getattr__(self, name: str) -> AsyncMethod[Result]:
        """Magic method dispatcher.

        Args:
            name: Name of the method to call.

        Returns:
            A method object.
        """
        return AsyncMethod(self.rpc, name)

    async def call(self, method: str, *params: Any) -> RPCResponse:
        """Get the raw response from an RPC method.

        Args:
            method: Name of the method to call.
            params: Positional arguments of the RPC method.

        Returns:
            An RPC result.
        """
        if method == GET_SESSION_KEY or method.startswith("system."):
            return await self._invoke(method, *params)

        # Methods requiring authentication
        return await self._invoke(method, self.key, *params)

    async def rpc(self, method: str, *params: Any) -> Result:
        """Execute a LimeSurvey RPC call with error handling.

        Args:
            method: Name of the method to call.
            params: Positional arguments of the RPC method.

        Returns:
            An RPC result.
        """
        response = await self.call(method, *params)
        handle_rpc_errors(response["result"], response["error"])
        return response["result"]

    async def _invoke(self, method: str, *params: Any) -> RPCResponse:
        """Execute a LimeSurvey RPC with a JSON payload.

        Args:
            method: Name of the method to call.
            params: Positional arguments of the RPC method.

        Returns:
            An RPC result.

        Raises:
            ResponseMismatchError: Request ID does not match the response ID.
            RPCInterfaceNotEnabledError: If the JSON RPC interface is not enabled
                (empty response).
            InvalidJSONResponseError: If the response is not valid JSON.
        """  # ruff: ignore[docstring-extraneous-exception]
        payload = prepare_request_payload(method, *params)

        res = await self._client.post(
            self.url,
            data=payload,
            headers={
                "content-type": "application/json",
            },
        )

        return handle_response(payload, res)

    async def close(self) -> None:
        """Close RPC session.

        Releases the session key with
        :ls_manual:`release_session_key <RemoteControl_2_API#release_session_key>`.
        """
        await self.release_session_key()
        await self._client.aclose()
        super()._close()

    async def __aenter__(self: Self) -> Self:
        """Context manager for RPC session.

        Returns:
            LimeSurvey RPC session.
        """
        self.__key: str | None = await self.get_session_key(
            self._username,
            self._password,
            self._auth_plugin,
        )

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
        await self.close()

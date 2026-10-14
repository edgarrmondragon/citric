# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Low level wrapper for connecting to the LSRC2."""

from __future__ import annotations

__lazy_modules__ = {
    "citric.exceptions",
    "citric.method",
    "citric.transport._default",
    "http",
    "json",
    "random",
    "threading",
    "warnings",
}

import http
import json
import logging
import random
import threading
import warnings
from importlib import metadata
from typing import TYPE_CHECKING, Any, Type  # ruff: ignore[deprecated-import]

from citric.exceptions import (
    InvalidJSONResponseError,
    LimeSurveyApiError,
    LimeSurveyStatusError,
    ResponseMismatchError,
)
from citric.method import Method
from citric.transport._default import _transport_or_default

if TYPE_CHECKING:
    import sys
    from types import TracebackType

    from citric.transport.protocol import HTTPResponse, HTTPTransport
    from citric.types import Result, RPCRequest, RPCResponse

    if sys.version_info >= (3, 11):
        from typing import Self
    else:
        from typing_extensions import Self

__all__ = ["Session"]

GET_SESSION_KEY = "get_session_key"

_CONNECT_FUTURE_WARNING = (
    "The default value of `connect` will change from True to False in a future "
    "version; pass `connect` explicitly to silence this warning"
)

logger: logging.Logger = logging.getLogger(__name__)


def _validate_rpc_response(request_id: int, data: RPCResponse) -> None:
    if (response_id := data["id"]) != request_id:
        msg = f"Response ID {response_id} does not match request ID {request_id}"
        raise ResponseMismatchError(msg)

    if (error := data["error"]) is not None:
        raise LimeSurveyApiError(error)


def _check_result_status(result: Any) -> None:  # ruff: ignore[any-type]
    if isinstance(result, dict) and result.get("status") not in {"OK", None}:
        raise LimeSurveyStatusError(
            result["status"],
            error_code=result.get("error_code"),
        )


class Session:
    """LimeSurvey RemoteControl 2 session.

    Upon creation, retrieves a session key with
    :ls_manual:`get_session_key <RemoteControl_2_API#get_session_key>` and stores it in
    the `key`_ attribute. With ``connect=False``, the key is instead retrieved the
    first time it is needed. The key is released upon session `closure`_.

    Args:
        url: LimeSurvey Remote Control endpoint.
        username: LimeSurvey user name.
        password: LimeSurvey password.
        transport: An HTTP transport implementing
            :class:`~citric.transport.protocol.HTTPTransport`, e.g. a
            :py:class:`requests.Session <requests.Session>` or
            :class:`~citric.transport.httpx2.Httpx2Transport`. Defaults to a new
            :py:class:`requests.Session <requests.Session>`.
        requests_session: Deprecated alias of ``transport``.
        auth_plugin: Name of the :ls_manual:`plugin <Authentication_plugins>` to use for
            authentication. For example,
            :ls_manual:`AuthLDAP <Authentication_plugins#LDAP>`. Defaults to using the
            :ls_manual:`internal database <Authentication_plugins#Internal_database>`
            (``"Authdb"``).
        json_encoder: A :py:class:`json.Encoder <json.JSONEncoder>` subclass to use for
            encoding RPC parameters.
        connect: Whether to authenticate right away. If ``False``, the session key is
            retrieved the first time it is needed. Deferred authentication is
            thread-safe: concurrent users of a not-yet-connected session authenticate
            only once. The credentials are kept in memory until the session connects
            or is closed. A future version will make ``False`` the default; until then,
            not passing ``connect`` explicitly emits a :py:class:`FutureWarning`.

    .. versionchanged:: 0.0.4
       Replaced the ``requests_session_factory`` parameter with ``requests_session``.

    .. versionadded:: 0.0.6
       Support Auth plugins with the ``auth_plugin`` parameter.

    .. versionadded:: 0.5.0
       The ``json_encoder`` parameter.

    .. version-changed:: NEXT_VERSION
        The ``requests_session`` parameter was deprecated, use ``transport`` instead.
        It also now accepts any object implementing
        :class:`~citric.transport.protocol.HTTPTransport`, not just
        :py:class:`requests.Session <requests.Session>`.

    .. version-added:: NEXT_VERSION
        The ``connect`` parameter.

    .. _key: #citric.session.Session.key
    .. _closure: #citric.session.Session.close
    """

    USER_AGENT = f"citric/{metadata.version('citric')}"

    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        *,
        auth_plugin: str = "Authdb",
        transport: HTTPTransport | None = None,
        requests_session: HTTPTransport | None = None,
        json_encoder: Type[json.JSONEncoder] | None = None,  # ruff: ignore[non-pep585-annotation]
        connect: bool | None = None,
    ) -> None:
        if connect is None:
            warnings.warn(_CONNECT_FUTURE_WARNING, FutureWarning, stacklevel=2)
            connect = True

        self.url: str = url
        self._transport = _transport_or_default(transport, requests_session)
        self._encoder = json_encoder or json.JSONEncoder
        self.__lock = threading.RLock()
        self.__closed = False
        self.__key: str | None = None
        self.__credentials: tuple[str, str, str] | None = (
            username,
            password,
            auth_plugin,
        )

        if connect:
            self._connect(self.__credentials)

    def _connect(self, credentials: tuple[str, str, str]) -> None:
        """Authenticate and store the session key."""
        username, password, auth_plugin = credentials
        self.__key = self.get_session_key(username, password, auth_plugin)
        self.__credentials = None

    @property
    def closed(self) -> bool:
        """Whether the RPC session is closed."""
        return self.__closed

    @property
    def key(self) -> str | None:
        """RPC session key.

        If the session was created with ``connect=False``, accessing this property
        authenticates with the server first.
        """
        with self.__lock:
            if self.__credentials is not None:
                self._connect(self.__credentials)
            return self.__key

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
        _check_result_status(response["result"])
        return response["result"]

    def _send_request(self, payload: RPCRequest) -> HTTPResponse:
        return self._transport.request(
            "POST",
            self.url,
            data=json.dumps(payload, cls=self._encoder),
            headers={
                "accept": "application/json",
                "content-type": "application/json",
                "User-Agent": self.USER_AGENT,
            },
        )

    def _invoke(self, method: str, *params: Any) -> RPCResponse:
        """Execute a LimeSurvey RPC with a JSON payload.

        Args:
            method: Name of the method to call.
            params: Positional arguments of the RPC method.

        Returns:
            An RPC result.

        Raises:
            LimeSurveyApiError: If the server responds with an error HTTP status code.
            InvalidJSONResponseError: If the response is not valid JSON.
        """
        request_id = random.randint(1, 999_999)  # ruff: ignore[suspicious-non-cryptographic-random-usage]

        res = self._send_request({
            "method": method,
            "params": [*params],
            "id": request_id,
        })
        if res.status_code >= http.HTTPStatus.BAD_REQUEST:
            msg = f"Request to LimeSurvey server failed with status {res.status_code}"
            raise LimeSurveyApiError(msg)

        data: RPCResponse

        try:
            data = res.json()
        except ValueError as e:
            raise InvalidJSONResponseError from e

        logger.info("Invoked RPC method %s with ID %d", method, request_id)
        _validate_rpc_response(request_id, data)

        return data

    def close(self) -> None:
        """Close RPC session.

        Releases the session key with
        :ls_manual:`release_session_key <RemoteControl_2_API#release_session_key>`.
        """
        # Wait for an in-flight deferred connection so its key gets released
        with self.__lock:
            if self.__key is not None:
                self.release_session_key()
            self._transport.close()
            self.__key = None
            self.__credentials = None
            self.__closed = True

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

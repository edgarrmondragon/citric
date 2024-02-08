"""Low level wrapper for connecting to the LSRC2."""

from __future__ import annotations

import json
import logging
import random
import typing as t
from importlib import metadata

import requests

from citric.exceptions import (
    InvalidJSONResponseError,
    LimeSurveyApiError,
    LimeSurveyStatusError,
    ResponseMismatchError,
    RPCInterfaceNotEnabledError,
)
from citric.method import Method

if t.TYPE_CHECKING:
    import sys
    from types import TracebackType

    from citric.types import Result, RPCResponse

    if sys.version_info >= (3, 11):
        from typing import Self  # noqa: ICN003
    else:
        from typing_extensions import Self

__all__ = ["Session"]

GET_SESSION_KEY = "get_session_key"

logger = logging.getLogger(__name__)


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
        raise LimeSurveyStatusError(result["status"])


class Session:
    """LimeSurvey RemoteControl 2 session.

    Upon creation, retrieves a session key with
    :ls_manual:`get_session_key <RemoteControl_2_API#get_session_key>` and stores it in
    the `key`_ attribute. The key is released upon session `closure`_.

    Args:
        url: LimeSurvey Remote Control endpoint.
        username: LimeSurvey user name.
        password: LimeSurvey password.
        requests_session: A :py:class:`requests.Session <requests.Session>` object.
        auth_plugin: Name of the :ls_manual:`plugin <Authentication_plugins>` to use for
            authentication. For example,
            :ls_manual:`AuthLDAP <Authentication_plugins#LDAP>`. Defaults to using the
            :ls_manual:`internal database <Authentication_plugins#Internal_database>`
            (``"Authdb"``).
        json_encoder: A :py:class:`json.Encoder <json.JSONEncoder>` subclass to use for
            encoding RPC parameters.

    .. versionchanged:: 0.0.4
       Replaced the ``requests_session_factory`` parameter with ``requests_session``.

    .. versionadded:: 0.0.6
       Support Auth plugins with the ``auth_plugin`` parameter.

    .. versionadded:: 0.5.0
       The ``json_encoder`` parameter.


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
        requests_session: requests.Session | None = None,
        json_encoder: type[json.JSONEncoder] | None = None,
    ) -> None:
        self.url = url
        self._session = requests_session or requests.session()
        self._session.headers["User-Agent"] = self.USER_AGENT
        self._encoder = json_encoder or json.JSONEncoder

        self.__key: str | None = self.get_session_key(
            username,
            password,
            auth_plugin,
        )

        self.__closed = False

    @property
    def closed(self) -> bool:
        """Whether the RPC session is closed."""
        return self.__closed

    @property
    def key(self) -> str | None:
        """RPC session key."""
        return self.__key

    def __getattr__(self, name: str) -> Method[Result]:
        """Magic method dispatcher."""
        return Method(self.rpc, name)

    def call(self, method: str, *params: t.Any) -> RPCResponse:
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

    def rpc(self, method: str, *params: t.Any) -> Result:
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

    def _invoke(self, method: str, *params: t.Any) -> RPCResponse:
        """Execute a LimeSurvey RPC with a JSON payload.

        Args:
            method: Name of the method to call.
            params: Positional arguments of the RPC method.

        Raises:
            ResponseMismatchError: Request ID does not match the response ID.
            RPCInterfaceNotEnabledError: If the JSON RPC interface is not enabled
                (empty response).
            InvalidJSONResponseError: If the response is not valid JSON.

        Returns:
            An RPC result.
        """
        request_id = random.randint(1, 999_999)  # noqa: S311

        payload = {
            "method": method,
            "params": [*params],
            "id": request_id,
        }

        res = self._session.post(
            self.url,
            data=json.dumps(payload, cls=self._encoder),
            headers={
                "content-type": "application/json",
            },
        )
        res.raise_for_status()

        if not res.text:
            raise RPCInterfaceNotEnabledError

        data: RPCResponse

        try:
            data = res.json()
        except json.JSONDecodeError as e:
            raise InvalidJSONResponseError from e

        logger.info("Invoked RPC method %s with ID %d", method, request_id)

        if (response_id := data["id"]) != request_id:
            msg = f"Response ID {response_id} does not match request ID {request_id}"
            raise ResponseMismatchError(msg)

        return data

    def close(self) -> None:
        """Close RPC session.

        Releases the session key with
        :ls_manual:`release_session_key <RemoteControl_2_API#release_session_key>`.
        """
        self.release_session_key()
        self._session.close()
        self.__key = None
        self.__closed = True

    def __enter__(self: Self) -> Self:
        """Context manager for RPC session.

        Returns:
            LimeSurvey RPC session.
        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
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

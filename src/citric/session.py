"""Low level wrapper for connecting to the LSRC2."""

from __future__ import annotations

import json
import logging
import random
import typing as t

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
    from types import TracebackType

    from citric.types import Result, RPCResponse

__all__ = ["Session"]

GET_SESSION_KEY = "get_session_key"
_T = t.TypeVar("_T", bound="Session")

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
    if isinstance(result, dict) and result.get("status") not in {"OK", None}:
        raise LimeSurveyStatusError(result["status"])

    if error is not None:
        raise LimeSurveyApiError(error)


class Session:
    """LimeSurvey RemoteControl 2 session.

    Upon creation, retrieves a session key with
    :ls_manual:`get_session_key <RemoteControl_2_API#get_session_key>` and stores it in
    the `key`_ attribute. The key is released upon session `closure`_.

    Args:
        url: LimeSurvey Remote Control endpoint.
        username: LimeSurvey user name.
        password: LimeSurvey password.
        requests_session: A `requests.Session`_ object.
        auth_plugin: Name of the :ls_manual:`plugin <Authentication_plugins>` to use for
            authentication. For example,
            :ls_manual:`AuthLDAP <Authentication_plugins#LDAP>`. Defaults to using the
            :ls_manual:`internal database <Authentication_plugins#Internal_database>`
            (``"Authdb"``).
        json_encoder: A `JSON encoder class <JSONEncoder>` to use for encoding RPC
            parameters.

    .. versionchanged:: 0.0.4
       Replaced the ``requests_session_factory`` parameter with ``requests_session``.

    .. versionadded:: 0.0.6
       Support Auth plugins with the ``auth_plugin`` parameter.

    .. versionadded:: 0.5.0
       The ``json_encoder`` parameter.


    .. _requests.Session:
        https://requests.readthedocs.io/en/latest/api/#request-sessions
    .. _key: #citric.session.Session.key
    .. _closure: #citric.session.Session.close
    .. _JSONEncoder: https://docs.python.org/3/library/json.html#json.JSONEncoder
    """

    _headers = {
        "user-agent": "citric-client",
    }

    __attrs__ = ["url", "key"]

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
        """Create a LimeSurvey RPC session."""
        self.url = url
        self._session = requests_session or requests.session()
        self._session.headers.update(self._headers)
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

    def rpc(self, method: str, *params: t.Any) -> Result:
        """Execute RPC method on LimeSurvey, with optional token authentication.

        Any method, except for `get_session_key`.

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

    def _invoke(
        self,
        method: str,
        *params: t.Any,
    ) -> Result:
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

        result = data["result"]
        error = data["error"]
        response_id = data["id"]
        logger.info("Invoked RPC method %s with ID %d", method, request_id)

        handle_rpc_errors(result, error)

        if response_id != request_id:
            msg = f"Response ID {response_id} does not match request ID {request_id}"
            raise ResponseMismatchError(msg)

        return result

    def close(self) -> None:
        """Close RPC session.

        Releases the session key with
        :ls_manual:`release_session_key <RemoteControl_2_API#release_session_key>`.
        """
        self.release_session_key()
        self._session.close()
        self.__key = None
        self.__closed = True

    def __enter__(self: _T) -> _T:
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

"""Low level wrapper for connecting to the LSRC2."""

from __future__ import annotations

import json
import logging
import random
from typing import TYPE_CHECKING, TypeVar

import requests

from citric.exceptions import (
    InvalidJSONResponseError,
    LimeSurveyApiError,
    LimeSurveyStatusError,
    ResponseMismatchError,
    RPCInterfaceNotEnabledError,
)
from citric.method import Method

if TYPE_CHECKING:
    from types import TracebackType
    from typing import Any

__all__ = ["Session"]

GET_SESSION_KEY = "get_session_key"
_T = TypeVar("_T", bound="Session")
logger = logging.getLogger(__name__)


def handle_rpc_errors(result: dict[str, Any], error: str | None) -> None:
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

    .. _requests.Session:
        https://requests.readthedocs.io/en/latest/api/#request-sessions
    .. _key: #citric.session.Session.key
    .. _closure: #citric.session.Session.close
    """

    _headers = {
        "content-type": "application/json",
        "user-agent": "citric-client",
    }

    __attrs__ = ["url", "key"]

    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        *,
        requests_session: requests.Session | None = None,
        auth_plugin: str = "Authdb",
    ) -> None:
        """Create a LimeSurvey RPC session."""
        self.url = url
        self._session = requests_session or requests.session()
        self._session.headers.update(self._headers)

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

    def __getattr__(self, name: str) -> Method:
        """Magic method dispatcher."""
        return Method(self.rpc, name)

    def rpc(self, method: str, *params: Any) -> Any:  # noqa: ANN401
        """Execute RPC method on LimeSurvey, with optional token authentication.

        Any method, except for `get_session_key`.

        Args:
            method: Name of the method to call.
            params: Positional arguments of the RPC method.

        Returns:
            An RPC result.
        """
        if method == GET_SESSION_KEY or method.startswith("system."):
            return self._invoke(self._session, self.url, method, *params)

        # Methods requiring authentication
        return self._invoke(self._session, self.url, method, self.key, *params)

    @staticmethod
    def _invoke(
        session: requests.Session,
        url: str,
        method: str,
        *params: Any,
    ) -> Any:  # noqa: ANN401
        """Execute a LimeSurvey RPC with a JSON payload.

        Args:
            session (requests.Session): An HTTP session for communication with
                the LSRC2 API.
            url: URL of the LSRC2 API.
            method (str): Name of the method to call.
            params (Any): Positional arguments of the RPC method.

        Raises:
            ResponseMismatchError: Request ID does not match the response ID.
            RPCInterfaceNotEnabledError: If the JSON RPC interface is not enabled
                (empty response).
            InvalidJSONResponseError: If the response is not valid JSON.

        Returns:
            Any: An RPC result.
        """
        request_id = random.randint(1, 999_999)

        payload = {
            "method": method,
            "params": [*params],
            "id": request_id,
        }

        res = session.post(url, json=payload)
        res.raise_for_status()

        if res.text == "":
            raise RPCInterfaceNotEnabledError

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

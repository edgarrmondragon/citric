"""Low level wrapper for connecting to the LSRC2."""
from types import TracebackType
from typing import Any, Optional, Type, TypeVar

import requests

from citric.response import RPCResponse


class BaseRPC:
    """Base class for executing RPC in the LimeSurvey."""

    def invoke(
        self, url: str, method: str, *args: Any, request_id: int = 1  # noqa: ANN101
    ) -> RPCResponse:
        """Execute a LimeSurvey RPC.

        Args:
            url: URL of LimeSurvey RPC interface.
            method: Name of the method to call.
            args: Positional arguments of the RPC method.
            request_id: Request ID for response validation.

        Raises:
            NotImplementedError: Subclass does not implement this method.
        """
        raise NotImplementedError


class JSONRPC(BaseRPC):
    """Execute JSON-RPC in LimeSurvey."""

    _headers = {
        "content-type": "application/json",
        "user-agent": "citric-client",
    }

    def __init__(self) -> None:  # noqa: ANN101
        """Create a JSON RPC object."""
        self.request_session = requests.Session()
        self.request_session.headers.update(self._headers)

    def invoke(
        self, url: str, method: str, *args: Any, request_id: int = 1,  # noqa: ANN101
    ) -> RPCResponse:
        """Execute a LimeSurvey RPC with a JSON payload.

        Args:
            url: URL of LimeSurvey RPC interface.
            method: Name of the method to call.
            args: Positional arguments of the RPC method.
            request_id: Request ID for response validation.

        Returns:
            An RPC response with result, error and id attributes.
        """
        payload = {
            "method": method,
            "params": [*args],
            "id": request_id,
        }

        res = self.request_session.post(url, json=payload)

        response = RPCResponse.parse_response(res)

        return response


T = TypeVar("T", bound="Session")


class Session(object):
    """LimeSurvey RemoteControl 2 API session.

    Args:
        url: LimeSurvey Remote Control endpoint.
        admin_user: LimeSurvey user name.
        admin_pass: LimeSurvey password.
        spec: RPC specification. By default JSON-RPC is used.
    """

    __attrs__ = ["url", "key"]

    def __init__(
        self,  # noqa: ANN101
        url: str,
        admin_user: str,
        admin_pass: str,
        spec: BaseRPC = JSONRPC(),
    ) -> None:
        """Create a LimeSurvey RPC session."""
        self.url = url
        self.spec = spec
        self.key = self.get_session_key(admin_user, admin_pass)

    def rpc(
        self, method: str, *args: Any, request_id: int = 1,  # noqa: ANN101
    ) -> RPCResponse:
        """Execute RPC method on LimeSurvey, with token authentication.

        Any method, except for `get_session_key`.

        Args:
            method: Name of the method to call.
            args: Positional arguments of the RPC method.
            request_id: Request ID for response validation.

        Returns:
            An RPC response with result, error and id attributes.
        """
        return self.spec.invoke(
            self.url, method, self.key, *args, request_id=request_id,
        )

    def get_session_key(
        self, admin_user: str, admin_pass: str, request_id: int = 1  # noqa: ANN101
    ) -> str:
        """Get RC API session key.

        Authenticate against the RPC interface.

        Args:
            admin_user: Admin username.
            admin_pass: Admin password.
            request_id: Request ID for response validation.

        Returns:
            A session key. This is mandatory for all following LSRC2 function calls.
        """
        response = self.spec.invoke(
            self.url, "get_session_key", admin_user, admin_pass, request_id=request_id,
        )

        return response.result

    def close(self) -> None:  # noqa: ANN101
        """Close RPC API session."""
        self.rpc("release_session_key")

    def __enter__(self: T) -> T:
        """Context manager for API session.

        Returns:
            LimeSurvey RPC session.
        """
        return self

    def __exit__(
        self,  # noqa: ANN101
        type: Optional[Type[BaseException]],
        value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        """Safely exit an API session.

        Args:
            type: Exception class.
            value: Exception instance.
            traceback: Error traceback.
        """
        self.close()

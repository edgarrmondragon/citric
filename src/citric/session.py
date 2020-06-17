"""Low level wrapper for connecting to the LSRC2."""
from types import TracebackType
from typing import Any, Optional, Type, TypeVar

from citric.response import RPCResponse
from citric.rpc.base import BaseRPC
from citric.rpc.json import JSONRPC


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
        response = self.spec.invoke(
            self.url, method, self.key, *args, request_id=request_id,
        )
        response.validate()

        return response

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
        response.validate()

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

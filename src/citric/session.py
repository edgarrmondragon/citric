"""Low level wrapper for connecting to the LSRC2."""
from types import TracebackType
from typing import Any, Optional, Type, TypeVar

from citric.method import Method
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
        self.__key: Optional[str] = self.get_session_key(admin_user, admin_pass)
        self.__closed = False

    @property
    def closed(self) -> bool:  # noqa: ANN101
        """Whether the RPC session is closed."""
        return self.__closed

    @property
    def key(self) -> Optional[str]:  # noqa: ANN101
        """RPC session key."""
        return self.__key

    def __getattr__(self, name: str) -> Method:  # noqa: ANN101
        """Magic method dispatcher."""
        return Method(self.rpc, name)

    def rpc(self, method: str, *params: Any) -> Any:  # noqa: ANN101
        """Execute RPC method on LimeSurvey, with optional token authentication.

        Any method, except for `get_session_key`.

        Args:
            method: Name of the method to call.
            params: Positional arguments of the RPC method.

        Returns:
            An RPC result.
        """
        if method == "get_session_key" or method.startswith("system."):
            result = self.spec.invoke(self.url, method, *params)
        # Methods requiring authentication
        else:
            result = self.spec.invoke(self.url, method, self.key, *params)

        return result

    def close(self) -> None:  # noqa: ANN101
        """Close RPC API session."""
        self.release_session_key()
        self.__key = None
        self.__closed = True

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

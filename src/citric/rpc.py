"""Low level wrapper for connecting to the LSRC2."""
from types import TracebackType
from typing import Any, Optional, Type, TypeVar

import requests

from citric.response import RPCResponse

B = TypeVar("B", bound="BaseRPC")
J = TypeVar("J", bound="JSONRPC")
S = TypeVar("S", bound="Session")


class BaseRPC:
    """Base class for executing RPC in the LimeSurvey."""

    def invoke(self: B) -> RPCResponse:
        raise NotImplementedError


class JSONRPC(BaseRPC):
    """Execute JSON-RPC in LimeSurvey."""

    _headers = {
        "content-type": "application/json",
        "user-agent": "citric-client",
    }

    def __init__(self: J) -> None:
        self.request_session = requests.Session()
        self.request_session.headers.update(self._headers)

    def invoke(
        self: J, url: str, method: str, *args: Any, request_id: int = 1,
    ) -> RPCResponse:

        payload = {
            "method": method,
            "params": [*args],
            "id": request_id,
        }

        res = self.request_session.post(url, json=payload)

        response = RPCResponse.parse_response(res)

        return response


class Session(object):
    """LimeSurvey RemoteControl 2 API session.

    :param url: LimeSurvey Remote Control endpoint.
    :type url: ``str``
    :param admin_user: LimeSurvey user name.
    :type admin_user: ``str``
    :param admin_pass: LimeSurvey password.
    :type admin_pass: ``str``
    :param spec: RPC specification
    :type spec: ``BaseRPC``
    """

    __attrs__ = ["url", "key"]

    def __init__(
        self: S, url: str, admin_user: str, admin_pass: str, spec: BaseRPC = JSONRPC(),
    ) -> None:
        """Create LimeSurvey wrapper."""
        self.url = url
        self.spec = spec
        self.key: str = self.get_session_key(admin_user, admin_pass)

    def rpc(self: S, method: str, *args: Any, request_id: int = 1) -> RPCResponse:
        r"""Authenticated execution of an RPC method on LimeSurvey.

        :param method: Name of the method to call.
        :type method: ``str``
        :param \*args: Postional arguments of the RPC method.
        :type \*args: ``Any``
        :param request_id: Request ID for response validation.
        :type request_id: ``int``
        """
        return self.spec.invoke(
            self.url, method, self.key, *args, request_id=request_id,
        )

    def get_session_key(
        self: S, admin_user: str, admin_pass: str, request_id: int = 1
    ) -> Any:
        """Get RC API session key.

        :param admin_user: LimeSurvey admin username.
        :type admin_user: ``str``
        :param admin_pass: LimeSurvey admin password.
        :type admin_pass: ``str``
        :param request_id: LimeSurvey RPC request ID.
        :type request_id: ``Any``
        """

        response = self.spec.invoke(
            self.url, "get_session_key", admin_user, admin_pass, request_id=request_id,
        )

        return response.result

    def close(self: S) -> None:
        """Close RC API session."""
        self.rpc("release_session_key")

    def __enter__(self: S) -> S:
        """Context manager for API session."""
        return self

    def __exit__(
        self: S,
        type: Optional[Type[BaseException]],
        value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        """Safely exit an API session."""
        self.close()

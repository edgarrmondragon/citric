"""XML-RPC implementation."""
from typing import Any
from xmlrpc.client import dumps, loads

from citric.rpc.base import BaseRPC


class XMLRPC(BaseRPC):
    """Execute XML-RPC in LimeSurvey."""

    _headers = {
        "content-type": "application/xml",
        "user-agent": "citric-client",
    }

    def __init__(self) -> None:  # noqa: ANN101
        """Create an XML-RPC interface."""
        super().__init__()

    def invoke(self, url: str, method: str, *params: Any) -> Any:  # noqa: ANN101
        """Execute a LimeSurvey RPC with a JSON payload.

        Args:
            url: URL of LimeSurvey RPC interface.
            method: Name of the method to call.
            params: Positional arguments of the RPC method.

        Returns:
            An RPC result.
        """
        payload = dumps(params, method)

        res = self.request_session.post(url, data=payload)
        self._check_non_empty_response(res.text)

        (result,), error = loads(res.text)
        self._check_result(result)
        self._check_error(error)

        return result

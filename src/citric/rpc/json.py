"""JSON-RPC implementation."""
from typing import Any

from citric.exceptions import LimeSurveyError
from citric.response import MethodResponse
from citric.rpc.base import BaseRPC


class JSONRPC(BaseRPC):
    """Execute JSON-RPC in LimeSurvey."""

    _headers = {
        "content-type": "application/json",
        "user-agent": "citric-client",
    }

    def __init__(self) -> None:  # noqa: ANN101
        """Create a JSON-RPC interface."""
        super().__init__()

    def invoke(
        self, url: str, method: str, *params: Any, request_id: int = 1,  # noqa: ANN101
    ) -> MethodResponse:
        """Execute a LimeSurvey RPC with a JSON payload.

        Args:
            url: URL of LimeSurvey RPC interface.
            method: Name of the method to call.
            params: Positional arguments of the RPC method.
            request_id: Request ID for response validation.

        Returns:
            An RPC response with result, error and id attributes.

        Raises:
            LimeSurveyError: Request ID does not match the response ID.
        """
        payload = {
            "method": method,
            "params": [*params],
            "id": request_id,
        }

        res = self.request_session.post(url, json=payload)
        self._check_non_empty_response(res.text)

        data = res.json()
        if data["id"] != request_id:
            message = "ID %s in response does not match the one in the request %s"
            raise LimeSurveyError(message % (data["id"], request_id))

        response = MethodResponse(result=data["result"], error=data["error"])

        return response

"""RPC Response."""

from typing import Any, NamedTuple, Optional, Type, TypeVar

import requests

from citric.exceptions import (
    LimeSurveyApiError,
    LimeSurveyError,
    LimeSurveyStatusError,
)

T = TypeVar("T", bound="RPCResponse")


class RPCResponse(NamedTuple):
    """LimeSurvey RPC response object.

    Args:
        result: RPC output.
        error: Error message, if any.
        id: RPC Request ID.
    """

    result: Any
    """RPC output."""

    error: Optional[str]
    """Error message."""

    id: int
    """RPC request ID."""

    @classmethod
    def parse_response(cls: Type[T], response: requests.Response) -> T:
        """Parse a requests response into an RPC response.

        A exception is raised when LimeSurvey responds with an empty message,
        an explicit error, or a bad status.

        Args:
            response: A response from the LimeSurvey JSON-RPC API.

        Returns:
            An RPC response with result, error and id attributes.

        Raises:
            LimeSurveyError: The API returned an empty response, meaning the
                RPC interface is not enabled.
            LimeSurveyStatusError: The result key from the response payload has
                a non-null status.
            LimeSurveyApiError: The response payload has a non-null error key.
        """
        if response.text == "":
            raise LimeSurveyError(msg="RPC interface not enabled")

        json_data = response.json()
        rpc = cls(**json_data)

        if isinstance(rpc.result, dict) and rpc.result.get("status") is not None:
            raise LimeSurveyStatusError(msg=rpc.result["status"])

        if rpc.error is not None:
            raise LimeSurveyApiError(msg=rpc.error)

        return rpc

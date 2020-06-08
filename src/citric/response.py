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

    :param result: RPC result.
    :param error: Error message, if any.
    :param id: RPC Request ID.
    """

    result: Any
    error: Optional[str]
    id: int

    @classmethod
    def parse_response(cls: Type[T], response: requests.Response) -> T:
        """Parse a requests response into an RPC response.

        A exception is raised when LimeSurvey responds with an empty message,
        an explicit error, or a bad status.
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

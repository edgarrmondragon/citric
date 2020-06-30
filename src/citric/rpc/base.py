"""Base class for all RPC client implementations."""
from typing import Any, Dict

import requests

from citric.exceptions import (
    LimeSurveyError,
    LimeSurveyStatusError,
    LimeSurveyApiError,
)


class BaseRPC:
    """Base class for executing RPC in the LimeSurvey."""

    _headers: Dict[str, Any] = {}

    def __init__(self) -> None:  # noqa: ANN101
        """Create an RPC interface."""
        self.request_session = requests.Session()
        self.request_session.headers.update(self._headers)

    def _check_non_empty_response(self, response_text: str) -> None:  # noqa: ANN101
        """Check if server response is empty.

        Args:
            response_text: Text of the method response.

        Raises:
            LimeSurveyError: The API returned an empty response, meaning the
                RPC interface is not enabled.
        """
        if response_text == "":
            raise LimeSurveyError("RPC interface not enabled")

    def _check_result(self, result: Any) -> None:  # noqa: ANN101
        """Check RPC result for status messages.

        Args:
            result: The RPC method output.

        Raises:
            LimeSurveyStatusError: The response key from the response payload has
                a non-null status.
        """
        if isinstance(result, dict) and result.get("status") not in {"OK", None}:
            raise LimeSurveyStatusError(result["status"])

    def _check_error(self, error: Any) -> None:  # noqa: ANN101
        """Check RPC if error is null.

        Args:
            error: An error generated by the RPC method.

        Raises:
            LimeSurveyApiError: The response payload has a non-null error key.
        """
        if error is not None:
            raise LimeSurveyApiError(error)

    def invoke(self, url: str, method: str, *params: Any) -> Any:  # noqa: ANN101
        """Execute a LimeSurvey RPC.

        Args:
            url: URL of LimeSurvey RPC interface.
            method: Name of the method to call.
            params: Positional arguments of the RPC method.

        Raises:
            NotImplementedError: Subclass does not implement this method.
        """
        raise NotImplementedError

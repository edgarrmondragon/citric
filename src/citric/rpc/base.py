"""Base class for all RPC client implementations."""
from typing import Any, Dict

import requests

from citric.exceptions import LimeSurveyError
from citric.response import MethodResponse


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
            raise LimeSurveyError(msg="RPC interface not enabled")

    def invoke(
        self, url: str, method: str, *args: Any, request_id: int = 1  # noqa: ANN101
    ) -> MethodResponse:
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

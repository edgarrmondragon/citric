"""RPC Response."""

from typing import Any, NamedTuple, Optional

from citric.exceptions import (
    LimeSurveyApiError,
    LimeSurveyStatusError,
)


class MethodResponse(NamedTuple):
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

    def validate(self) -> None:  # noqa: ANN101
        """Validate RPC method response.

        Raises:
            LimeSurveyStatusError: The result key from the response payload has
                a non-null status.
            LimeSurveyApiError: The response payload has a non-null error key.
        """
        if isinstance(self.result, dict) and self.result.get("status") is not None:
            raise LimeSurveyStatusError(msg=self.result["status"])

        if self.error is not None:
            raise LimeSurveyApiError(msg=self.error)

"""Common exceptions."""

from __future__ import annotations


class ResponseMismatchError(Exception):
    """Exception raised when request and response ID don't match."""


class LimeSurveyError(Exception):
    """Basic exception raised by LimeSurvey."""

    def __init__(self, message: str) -> None:
        """Create a generic error for the LimeSurvey RPC API.

        Args:
            message: Exception message. By default none, and a generic message is used.
        """
        super().__init__(message)


class LimeSurveyStatusError(LimeSurveyError):
    """Exception raised when LimeSurvey responds with an error status."""


class LimeSurveyApiError(LimeSurveyError):
    """Exception raised when LimeSurvey responds with a non-null error."""


class RPCInterfaceNotEnabledError(LimeSurveyError):
    """RPC interface not enabled on LimeSurvey."""

    def __init__(self) -> None:
        """Create a new exception."""
        super().__init__("RPC interface not enabled")


class InvalidJSONResponseError(LimeSurveyError):
    """RPC interface maybe not enabled on LimeSurvey."""

    def __init__(self) -> None:
        """Create a new exception."""
        msg = (
            "Received a non-JSON response, verify that the JSON RPC interface is "
            "enabled in global settings"
        )
        super().__init__(msg)

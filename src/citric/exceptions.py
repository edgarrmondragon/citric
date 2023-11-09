"""Common exceptions."""

from __future__ import annotations


class ResponseMismatchError(Exception):
    """Exception raised when request and response ID don't match."""


class LimeSurveyError(Exception):
    """Basic exception raised by LimeSurvey.

    Args:
        message: Exception message. By default none, and a generic message is used.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class LimeSurveyStatusError(LimeSurveyError):
    """Exception raised when LimeSurvey responds with an error status."""


class LimeSurveyApiError(LimeSurveyError):
    """Exception raised when LimeSurvey responds with a non-null error."""


class RPCInterfaceNotEnabledError(LimeSurveyError):
    """RPC interface not enabled on LimeSurvey."""

    def __init__(self) -> None:
        super().__init__("RPC interface not enabled")


class InvalidJSONResponseError(LimeSurveyError):
    """RPC interface maybe not enabled on LimeSurvey."""

    def __init__(self) -> None:
        msg = (
            "Received a non-JSON response, verify that the JSON RPC interface is "
            "enabled in global settings"
        )
        super().__init__(msg)

"""Common exceptions."""

from typing import Optional, TypeVar

from citric.response import RPCResponse

T = TypeVar("T", bound="LimeSurveyError")


class LimeSurveyError(Exception):
    """Basic exception raised by LimeSurvey."""

    default = "An error occured while requesting data from the LSRC2 API."

    def __init__(self: T, msg: Optional[str] = None) -> None:
        if msg is None:
            msg = self.default
        super(LimeSurveyError, self).__init__(msg)


class LimeSurveyStatusError(LimeSurveyError):
    """Exception raised when LimeSurvey responds with an error status."""

    def __init__(self: T, response: RPCResponse, msg: Optional[str] = None) -> None:
        super(LimeSurveyStatusError, self).__init__(msg=response.result["status"])
        self.response = response


class LimeSurveyApiError(LimeSurveyError):
    """Exception raised when LimeSurvey responds with a non-null error."""

    def __init__(self: T, response: RPCResponse, msg: Optional[str] = None) -> None:
        super(LimeSurveyApiError, self).__init__(msg=response.error)
        self.response = response

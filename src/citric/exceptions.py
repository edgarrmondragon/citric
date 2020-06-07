"""Common exceptions."""

from typing import Optional, TypeVar

T = TypeVar("T", bound="LimeSurveyError")


class LimeSurveyError(Exception):
    """Basic exception raised by LimeSurvey."""

    default = "An error occured while requesting data from the LSRC2 API."

    def __init__(self, msg: Optional[str] = None) -> None:  # noqa:: ANN101
        if msg is None:
            msg = self.default
        super(LimeSurveyError, self).__init__(msg)


class LimeSurveyStatusError(LimeSurveyError):
    """Exception raised when LimeSurvey responds with an error status."""


class LimeSurveyApiError(LimeSurveyError):
    """Exception raised when LimeSurvey responds with a non-null error."""

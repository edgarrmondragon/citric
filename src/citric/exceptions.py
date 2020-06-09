"""Common exceptions."""

from typing import Optional


class LimeSurveyError(Exception):
    """Basic exception raised by LimeSurvey."""

    default = "An error occured while requesting data from the LSRC2 API."

    def __init__(self, msg: Optional[str] = None) -> None:  # noqa:: ANN101
        """Create a generic error for the LimeSurvey RPC API.

        Args:
            msg: Exception message. By default none, and a generic message is used.
        """
        if msg is None:
            msg = self.default
        super(LimeSurveyError, self).__init__(msg)


class LimeSurveyStatusError(LimeSurveyError):
    """Exception raised when LimeSurvey responds with an error status."""


class LimeSurveyApiError(LimeSurveyError):
    """Exception raised when LimeSurvey responds with a non-null error."""

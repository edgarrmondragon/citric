"""Common exceptions."""


class LimeSurveyError(Exception):
    """Basic exception raised by LimeSurvey."""

    default = "An error occured while requesting data from the LSRC2 API."

    def __init__(self, msg=None):
        if msg is None:
            msg = self.default
        super(LimeSurveyError, self).__init__(msg)


class LimeSurveyStatusError(LimeSurveyError):
    """Exception raised when LimeSurvey responds with an error status."""

    def __init__(self, response, msg=None):
        super(LimeSurveyStatusError, self).__init__(msg=response.result["status"])
        self.response = response


class LimeSurveyApiError(LimeSurveyError):
    """Exception raised when LimeSurvey responds with a non-null error."""

    def __init__(self, response, msg=None):
        super(LimeSurveyApiError, self).__init__(msg=response.error)
        self.response = response

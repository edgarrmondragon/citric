"""RPC Response."""

from typing import Any, Callable, NamedTuple, Optional

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


class Method:
    """RPC method."""

    def __init__(
        self, caller: Callable[[str, Any], MethodResponse], name: str  # noqa: ANN101
    ) -> None:
        """Instantiate an RPC method."""
        self.__caller = caller
        self.__name = name

    def __getattr__(self, name: str) -> "Method":  # noqa: ANN101
        """Get nested method."""
        return Method(self.__caller, "%s.%s" % (self.__name, name))

    def __call__(self, *params: Any) -> MethodResponse:  # noqa: ANN101
        """Call RPC method.

        Args:
            params: RPC method parameters.

        Returns:
            A method response.
        """
        return self.__caller(self.__name, *params)

"""RPC methods."""

from typing import Any, Callable


class Method:
    """RPC method."""

    def __init__(self, caller: Callable, name: str) -> None:
        """Instantiate an RPC method."""
        self.__caller = caller
        self.__name = name

    def __getattr__(self, name: str) -> "Method":  # noqa: ANN101
        """Get nested method."""
        return Method(self.__caller, f"{self.__name}.{name}")

    def __call__(self, *params: Any) -> Any:  # noqa: ANN101
        """Call RPC method.

        Args:
            params: RPC method parameters.

        Returns:
            An RPC result.
        """
        return self.__caller(self.__name, *params)

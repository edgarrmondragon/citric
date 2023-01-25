"""RPC methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Callable


class Method:
    """RPC method."""

    def __init__(self, caller: Callable, name: str) -> None:
        """Instantiate an RPC method."""
        self.__caller = caller
        self.__name = name

    def __getattr__(self, name: str) -> Method:
        """Get nested method.

        Args:
            name: Method name.

        Returns:
            A new instance of Method for the nested call.

        >>> method = Method(print, "some_method")
        >>> method.nested("x", "y")
        some_method.nested x y
        """
        return Method(self.__caller, f"{self.__name}.{name}")

    def __call__(self, *params: Any) -> Any:  # noqa: ANN401
        """Call RPC method.

        Args:
            params: RPC method parameters.

        Returns:
            An RPC result.

        >>> method = Method(print, "some_method")
        >>> method(1, "a")
        some_method 1 a
        """
        return self.__caller(self.__name, *params)

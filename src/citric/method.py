"""RPC methods."""

from __future__ import annotations

from typing import Any, Callable, Generic, TypeVar

__all__ = ["Method"]

T = TypeVar("T")


class Method(Generic[T]):
    """RPC method.

    Args:
        caller: RPC caller function.
        name: RPC method name.
    """

    def __init__(self, caller: Callable[[str], T], name: str) -> None:
        self.__caller = caller
        self.__name = name

    def __getattr__(self, name: str) -> Method[T]:
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

    def __call__(self, *params: Any) -> T:
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

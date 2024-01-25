"""Test compatibility helpers."""

from __future__ import annotations

import pytest

from citric._compat import (
    FutureVersionWarning,  # noqa: PLC2701
    future,  # noqa: PLC2701
    future_parameter,  # noqa: PLC2701
)


@future("4.0.0")
def my_function() -> None:
    """A simple function."""


@future_parameter("4.0.0", "new_param")
def function_new_param(new_param: str | None = None) -> None:
    """A simple function."""


def test_dev_only():
    """Test that calling a dev-only functions raise a warning."""
    with pytest.warns(
        FutureVersionWarning,
        match="Method my_function is only supported .* 4.0.0",
    ):
        my_function()


def test_dev_only_param():
    """Test that calling a dev-only function parameters raise a warning."""
    # Calling with the default value should not raise a warning
    function_new_param()

    with pytest.warns(
        FutureVersionWarning,
        match="Parameter new_param is only supported .* 4.0.0",
    ):
        function_new_param(new_param="test")

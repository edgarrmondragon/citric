"""Test compatibility helpers."""

from __future__ import annotations

import pytest

from citric._compat import FutureVersionWarning, unreleased


@unreleased("4.0.0")
def my_function():
    """A simple function."""


def test_dev_only():
    """Test that dev_only raises a warning."""
    with pytest.warns(
        FutureVersionWarning,
        match="Method my_function is only supported .* 4.0.0",
    ):
        my_function()

# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Test package metadata."""

import pathlib
import sys
from importlib.metadata import version

from packaging.specifiers import SpecifierSet
from packaging.version import Version

import citric

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def test_version() -> None:
    """Test that the version in __init__.py matches the version in pyproject.toml."""
    assert version("citric") == citric.__version__, (
        f"Version in __init__.py ({citric.__version__}) does not "
        f"match version in pyproject.toml ({version('citric')})"
    )


def test_python_classifiers() -> None:
    """Test that the Python classifiers and requires-python in pyproject.toml match."""
    with pathlib.Path("pyproject.toml").open("rb") as f:
        data = tomllib.load(f)

    versions = (
        Version(x.split(" :: ")[-1])
        for x in data["project"]["classifiers"]
        if x.startswith("Programming Language :: Python :: 3.")
    )
    requires_python = SpecifierSet(data["project"]["requires-python"])
    assert all(v in requires_python for v in versions)

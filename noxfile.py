"""Nox configuration."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from nox import Session, session

FORCE_COLOR = "FORCE_COLOR"
TEST_DEPS = ["coverage[toml]", "faker", "pytest"]

package = "citric"

python_versions = ["3.11", "3.10", "3.9", "3.8", "3.7"]
pypy_versions = ["pypy3.7", "pypy3.8", "pypy3.9"]
all_python_versions = python_versions + pypy_versions

main_cpython_version = "3.11"
main_pypy_version = "pypy3.9"

locations = "src", "tests", "noxfile.py", "docs/conf.py"


@session(python=all_python_versions, tags=["test"])
def tests(session: Session) -> None:
    """Execute pytest tests and compute coverage."""
    env = {
        "PIP_CONSTRAINT": "requirements.txt",
        "PIP_ONLY_BINARY": ":all:",
    }

    if session.python == "3.13":
        env["PIP_NO_BINARY"] = "coverage"

    session.install(".[test]", env=env)
    args = session.posargs or ["-m", "not integration_test"]

    try:
        session.run("coverage", "run", "--parallel", "-m", "pytest", *args)
    finally:
        if session.interactive:
            session.notify("coverage", posargs=[])


@session(python=[main_cpython_version, main_pypy_version], tags=["test"])
def integration(session: Session) -> None:
    """Execute integration tests and compute coverage."""
    session.install(
        ".[test]",
        env={"PIP_CONSTRAINT": "requirements.txt"},
    )
    args = [
        "coverage",
        "run",
        "--parallel",
        "-m",
        "pytest",
        "-m",
        "integration_test",
    ]

    try:
        session.run(*args, *session.posargs)
    finally:
        if session.interactive:
            session.notify("coverage", posargs=[])


@session(python=[main_cpython_version, main_pypy_version], tags=["test"])
def xdoctest(session: Session) -> None:
    """Run examples with xdoctest."""
    if session.posargs:
        args = [package, *session.posargs]
    else:
        args = [f"--modname={package}", "--command=all"]
        if FORCE_COLOR in os.environ:
            args.append("--colored=1")

    session.install(".[test]")
    session.run("python", "-m", "xdoctest", *args)


@session()
def coverage(session: Session) -> None:
    """Upload coverage data."""
    args = session.posargs or ["report"]

    session.install(
        "coverage[toml]",
        env={"PIP_CONSTRAINT": "requirements.txt"},
    )

    if not session.posargs and any(Path().glob(".coverage.*")):
        session.run("coverage", "combine")

    session.run("coverage", *args)


@session(name="docs-build")
def docs_build(session: Session) -> None:
    """Build the documentation."""
    args = session.posargs or ["docs", "build"]
    if not session.posargs and FORCE_COLOR in os.environ:
        args.insert(0, "--color")

    session.install(
        ".[docs]",
        env={"PIP_CONSTRAINT": "requirements.txt"},
    )

    build_dir = Path("build")
    if build_dir.exists():
        shutil.rmtree(build_dir)

    session.run("sphinx-build", *args)


@session(name="docs-serve")
def docs_serve(session: Session) -> None:
    """Build the documentation."""
    args = session.posargs or [
        "--open-browser",
        "--watch",
        ".",
        "--ignore",
        "**/.nox/*",
        "--ignore",
        "**/.mypy_cache/*",
        "docs",
        "build",
    ]
    session.install(
        ".[docs]",
        env={"PIP_CONSTRAINT": "requirements.txt"},
    )

    build_dir = Path("build")
    if build_dir.exists():
        shutil.rmtree(build_dir)

    session.run("sphinx-autobuild", *args)

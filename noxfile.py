"""Nox configuration."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from textwrap import dedent

try:
    from nox_poetry import Session, session
except ImportError:
    message = f"""\
    Nox failed to import the 'nox-poetry' package.
    Please install it using the following command:
    {sys.executable} -m pip install nox-poetry"""
    raise SystemExit(dedent(message)) from None

GH_ACTIONS_ENV_VAR = "GITHUB_ACTIONS"
FORCE_COLOR = "FORCE_COLOR"
TEST_DEPS = ["coverage[toml]", "faker", "pytest"]

package = "citric"

python_versions = ["3.11", "3.10", "3.9", "3.8", "3.7"]
pypy_versions = ["pypy3.7", "pypy3.8", "pypy3.9", "pypy3.10"]
all_python_versions = python_versions + pypy_versions

main_cpython_version = "3.11"
main_pypy_version = "pypy3.9"

locations = "src", "tests", "noxfile.py", "docs/conf.py"


@session(python=all_python_versions, tags=["test"])
def tests(session: Session) -> None:
    """Execute pytest tests and compute coverage."""
    deps = [*TEST_DEPS]
    env = {"PIP_ONLY_BINARY": ":all:"}

    if GH_ACTIONS_ENV_VAR in os.environ:
        deps.append("pytest-github-actions-annotate-failures")

    if session.python in ("3.13", "pypy3.10"):
        env["PIP_NO_BINARY"] = "coverage"

    session.install(".", env=env)
    session.install(*deps, env=env)
    args = session.posargs or ["-m", "not integration_test"]

    try:
        session.run("coverage", "run", "--parallel", "-m", "pytest", *args)
    finally:
        if session.interactive:
            session.notify("coverage", posargs=[])


@session(python=[main_cpython_version, main_pypy_version], tags=["test"])
def integration(session: Session) -> None:
    """Execute integration tests and compute coverage."""
    deps = [*TEST_DEPS]
    if GH_ACTIONS_ENV_VAR in os.environ:
        deps.append("pytest-github-actions-annotate-failures")

    session.install(".")
    session.install(*deps)

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

    session.install(".")
    session.install("xdoctest[colors]")
    session.run("python", "-m", "xdoctest", *args)


@session()
def coverage(session: Session) -> None:
    """Upload coverage data."""
    args = session.posargs or ["report"]

    session.install("coverage[toml]")

    if not session.posargs and any(Path().glob(".coverage.*")):
        session.run("coverage", "combine")

    session.run("coverage", *args)


@session(python=python_versions, tags=["lint"])
def mypy(session: Session) -> None:
    """Type-check using mypy."""
    args = session.posargs or locations
    session.install(
        ".",
        "faker",
        "mypy",
        "pytest",
        "sphinx",
        "types-requests",
        "typing-extensions",
    )
    session.run("mypy", *args)


@session(name="docs-build")
def docs_build(session: Session) -> None:
    """Build the documentation."""
    args = session.posargs or ["docs", "build"]
    if not session.posargs and FORCE_COLOR in os.environ:
        args.insert(0, "--color")

    session.install(".[docs]")

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
    session.install(".[docs]")

    build_dir = Path("build")
    if build_dir.exists():
        shutil.rmtree(build_dir)

    session.run("sphinx-autobuild", *args)


@session(name="api")
def api_changes(session: Session) -> None:
    """Check for API changes."""
    args = [
        "griffe",
        "check",
        "citric",
        "-s=src",
    ]

    if session.posargs:
        args.append(f"-a={session.posargs[0]}")

    session.run(*args, external=True)

"""Nox configuration."""

from __future__ import annotations

import os
import shutil
import typing as t
from pathlib import Path

import nox

GH_ACTIONS_ENV_VAR = "GITHUB_ACTIONS"
FORCE_COLOR = "FORCE_COLOR"
TEST_DEPS = ["coverage[toml]", "faker", "pytest"]

package = "citric"

python_versions = ["3.11", "3.10", "3.9", "3.8", "3.7"]
pypy_versions = ["pypy3.7", "pypy3.8", "pypy3.9"]
all_python_versions = python_versions + pypy_versions

main_cpython_version = "3.11"
main_pypy_version = "pypy3.9"

locations = "src", "tests", "noxfile.py", "docs/conf.py"


def install(
    session: nox.Session,
    *,
    groups: t.Iterable[str],
    root: bool = True,
) -> None:
    """Install the dependency groups using Poetry.

    This function installs the given dependency groups into the session's
    virtual environment. When ``root`` is true (the default), the function
    also installs the root package and its default dependencies.
    To avoid an editable install, the root package is not installed using
    ``poetry install``. Instead, the function invokes ``pip install .``
    to perform a PEP 517 build.

    Args:
        session: The Session object.
        groups: The dependency groups to install.
        root: Install the root package.
    """
    session.run_always(
        "poetry",
        "install",
        "--no-root",
        "--sync",
        f'--{"with" if root else "only"}={",".join(groups)}',
        external=True,
    )
    if root:
        session.install(".")


@nox.session(python=all_python_versions, tags=["test"])
def tests(session: nox.Session) -> None:
    """Execute pytest tests and compute coverage."""
    install(session, groups=["dev"], root=True)
    args = session.posargs or ["-m", "not integration_test"]

    try:
        session.run("coverage", "run", "--parallel", "-m", "pytest", *args)
    finally:
        if session.interactive:
            session.notify("coverage", posargs=[])


@nox.session(python=[main_cpython_version, main_pypy_version], tags=["test"])
def integration(session: nox.Session) -> None:
    """Execute integration tests and compute coverage."""
    deps = [*TEST_DEPS]
    if GH_ACTIONS_ENV_VAR in os.environ:
        deps.append("pytest-github-actions-annotate-failures")

    install(session, groups=["dev"], root=True)

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


@nox.session(python=[main_cpython_version, main_pypy_version], tags=["test"])
def xdoctest(session: nox.Session) -> None:
    """Run examples with xdoctest."""
    if session.posargs:
        args = [package, *session.posargs]
    else:
        args = [f"--modname={package}", "--command=all"]
        if FORCE_COLOR in os.environ:
            args.append("--colored=1")

    install(session, groups=["dev"], root=True)
    session.run("python", "-m", "xdoctest", *args)


@nox.session()
def coverage(session: nox.Session) -> None:
    """Upload coverage data."""
    args = session.posargs or ["report"]

    install(session, groups=["dev"], root=False)

    if not session.posargs and any(Path().glob(".coverage.*")):
        session.run("coverage", "combine")

    session.run("coverage", *args)


@nox.session(name="docs-build")
def docs_build(session: nox.Session) -> None:
    """Build the documentation."""
    args = session.posargs or ["docs", "build"]
    if not session.posargs and FORCE_COLOR in os.environ:
        args.insert(0, "--color")

    install(session, groups=["dev"], root=False)

    build_dir = Path("build")
    if build_dir.exists():
        shutil.rmtree(build_dir)

    session.run("sphinx-build", *args)


@nox.session(name="docs-serve")
def docs_serve(session: nox.Session) -> None:
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
    install(session, groups=["dev"], root=False)

    build_dir = Path("build")
    if build_dir.exists():
        shutil.rmtree(build_dir)

    session.run("sphinx-autobuild", *args)

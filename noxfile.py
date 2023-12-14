"""Nox configuration."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from nox import Session, session

GH_ACTIONS_ENV_VAR = "GITHUB_ACTIONS"
FORCE_COLOR = "FORCE_COLOR"

package = "citric"

python_versions = ["3.12", "3.11", "3.10", "3.9", "3.8"]
pypy_versions = ["pypy3.9", "pypy3.10"]
all_python_versions = python_versions + pypy_versions

main_cpython_version = "3.12"
main_pypy_version = "pypy3.9"

locations = "src", "tests", "noxfile.py", "docs/conf.py"


@session(python=all_python_versions, tags=["test"])
def tests(session: Session) -> None:
    """Execute pytest tests and compute coverage."""
    env = {"PIP_ONLY_BINARY": ":all:"}

    if session.python == "3.13":
        env["PIP_NO_BINARY"] = "coverage,MarkupSafe"

    if session.python.startswith("pypy"):
        env["PIP_NO_BINARY"] = "MarkupSafe"

    session.install(".[tests]", env=env)
    args = session.posargs or ["-m", "not integration_test"]

    try:
        session.run("coverage", "run", "-m", "pytest", *args)
    finally:
        if session.interactive:
            session.notify("coverage", posargs=[])


@session(python=[main_cpython_version, main_pypy_version], tags=["test"])
def integration(session: Session) -> None:
    """Execute integration tests and compute coverage."""
    session.install(".[tests]")

    args = [
        "coverage",
        "run",
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
        session.run("coverage", "combine", "--debug=pathmap")

    session.run("coverage", *args)


@session(name="deps", python=python_versions)
def dependencies(session: Session) -> None:
    """Check issues with dependencies."""
    session.install(".")
    session.install("deptry")
    session.run("deptry", "src")


@session(python=python_versions, tags=["lint"])
def mypy(session: Session) -> None:
    """Type-check using mypy."""
    args = session.posargs or locations
    session.install(".[typing]")
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


@session(name="generate-tags", tags=["status"])
def tags(session: Session) -> None:
    """Print tags."""
    session.install("requests", "requests-cache")
    session.run("python", "scripts/docker_tags.py")

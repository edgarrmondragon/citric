"""Nox configuration."""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path
from textwrap import dedent

import nox

try:
    from nox_poetry import Session, session
except ImportError:
    message = f"""\
    Nox failed to import the 'nox-poetry' package.
    Please install it using the following command:
    {sys.executable} -m pip install nox-poetry"""
    raise SystemExit(dedent(message)) from None

package = "citric"
python_versions = ["3.11", "3.10", "3.9", "3.8", "3.7"]
pypy_versions = ["pypy3.9"]
main_python_version = "3.10"
locations = "src", "tests", "noxfile.py", "docs/conf.py"
nox.options.sessions = (
    "lint",
    "black-check",
    "safety",
    "mypy",
    "tests",
    "pytype",
    "xdoctest",
)


def install_with_constraints(session: Session, *args, **kwargs) -> None:
    """Install individual packages with Poetry version constraints."""
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            f"--output={requirements.name}",
            external=True,
        )
        session.install(f"--constraint={requirements.name}", *args, **kwargs)


@session(python=main_python_version)
def safety(session: Session) -> None:
    """Check if packages are safe."""
    requirements = session.poetry.export_requirements()
    session.install("safety")
    session.run("safety", "check", "--full-report", f"--file={requirements}")


@session(python=python_versions)
def mypy(session: Session) -> None:
    """Check types with mypy."""
    args = session.posargs or ["src", "tests", "docs/conf.py"]
    session.install(".")
    session.install(
        "mypy",
        "pytest",
        "types-requests",
        "types-psycopg2",
    )
    session.run("mypy", *args)
    if not session.posargs:
        session.run("mypy", f"--python-executable={sys.executable}", "noxfile.py")


@session(python=python_versions + pypy_versions)
def tests(session: Session) -> None:
    """Execute pytest tests and compute coverage."""
    session.install(".")
    session.install("coverage[toml]", "pytest")
    args = session.posargs or ["-m", "not integration_test"]

    try:
        session.run("coverage", "run", "--parallel", "-m", "pytest", *args)
    finally:
        if session.interactive:
            session.notify("coverage", posargs=[])


@session(python=python_versions + pypy_versions)
def integration(session: Session) -> None:
    """Execute integration tests and compute coverage."""
    session.install(".")
    session.install("coverage[toml]", "pytest", "psycopg2-binary")
    try:
        session.run(
            "coverage",
            "run",
            "--parallel",
            "-m",
            "pytest",
            "-m",
            "integration_test",
            *session.posargs,
        )
    finally:
        if session.interactive:
            session.notify("coverage", posargs=[])


@session(python="3.7")
def pytype(session: Session) -> None:
    """Infer and check types with pytype."""
    args = session.posargs or ["--disable=import-error", *locations]
    session.install("pytype")
    session.run("pytype", *args)


@session(python=main_python_version)
def typeguard(session: Session) -> None:
    """Runtime type checking using Typeguard."""
    session.install(".")
    session.install("pytest", "typeguard", "pygments", "psycopg2-binary")
    session.run("pytest", *session.posargs)


@session(python=python_versions)
def xdoctest(session: Session) -> None:
    """Run examples with xdoctest."""
    if session.posargs:
        args = [package, *session.posargs]
    else:
        args = [f"--modname={package}", "--command=all"]
        if "FORCE_COLOR" in os.environ:
            args.append("--colored=1")

    session.install(".")
    session.install("xdoctest[colors]")
    session.run("python", "-m", "xdoctest", *args)


@session(python=main_python_version)
def coverage(session: Session) -> None:
    """Upload coverage data."""
    args = session.posargs or ["report"]

    session.install("coverage[toml]")

    if not session.posargs and any(Path().glob(".coverage.*")):
        session.run("coverage", "combine")

    session.run("coverage", *args)


@session(python=python_versions)
def lint(session: Session) -> None:
    """Check code linting."""
    args = session.posargs or locations
    session.install(
        "flake8",
        "flake8-annotations",
        "flake8-black",
        "flake8-docstrings",
        "flake8-isort",
        "darglint",
    )
    session.run("flake8", *args)


@session(name="black-fix", python=main_python_version)
def black_fix(session: Session) -> None:
    """Format code."""
    args = session.posargs or locations
    session.install("black")
    session.run("black", *args)


@session(name="black-check", python=python_versions)
def black_check(session: Session) -> None:
    """Check code format."""
    args = session.posargs or locations
    session.install("black")
    session.run("black", "--check", *args)


@session(name="docs-build", python=main_python_version)
def docs_build(session: Session) -> None:
    """Build the documentation."""
    args = session.posargs or ["docs", "build"]
    if not session.posargs and "FORCE_COLOR" in os.environ:
        args.insert(0, "--color")

    session.install(".[docs]")

    build_dir = Path("build")
    if build_dir.exists():
        shutil.rmtree(build_dir)

    session.run("sphinx-build", *args)


@session(name="docs-serve", python=main_python_version)
def docs_serve(session: Session) -> None:
    """Build the documentation."""
    args = session.posargs or [
        "--open-browser",
        "--watch",
        ".",
        "--ignore",
        "**/.nox/*",
        "docs",
        "build",
    ]
    session.install(".[docs]")

    build_dir = Path("build")
    if build_dir.exists():
        shutil.rmtree(build_dir)

    session.run("sphinx-autobuild", *args)

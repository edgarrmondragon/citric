"""Nox configuration."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import nox

GH_ACTIONS_ENV_VAR = "GITHUB_ACTIONS"
FORCE_COLOR = "FORCE_COLOR"

nox.options.sessions = [
    "tests",
    "xdoctest",
    "deps",
    "mypy",
    "docs-build",
    "api",
]
nox.needs_version = ">=2024.4.15"
nox.options.default_venv_backend = "uv"

package = "citric"

python_versions = [
    "3.13",
    "3.12",
    "3.11",
    "3.10",
    "3.9",
    "3.8",
]
pypy_versions = ["pypy3.10"]
all_python_versions = python_versions + pypy_versions

locations = "src", "tests", "noxfile.py", "docs/conf.py"


def _run_tests(session: nox.Session, *args: str) -> None:
    env = {"COVERAGE_CORE": "sysmon"}
    try:
        session.run("coverage", "run", "-m", "pytest", *args, env=env)
    finally:
        if session.interactive:
            session.notify("coverage", posargs=[])


@nox.session(python=python_versions, tags=["test"])
@nox.parametrize("constraints", ["highest", "lowest-direct"])
def tests(session: nox.Session, constraints: str) -> None:
    """Execute pytest tests and compute coverage."""
    install_args = ["citric[tests] @ ."]
    if constraints == "lowest-direct":
        install_args.extend(["-c", "requirements/requirements-lowest-direct.txt"])

    session.install(*install_args)
    args = session.posargs or ["-m", "not integration_test"]
    _run_tests(session, *args)


@nox.session(tags=["test"])
def integration(session: nox.Session) -> None:
    """Execute integration tests and compute coverage."""
    session.install("citric[tests] @ .")
    args = session.posargs or ["-m", "integration_test"]
    _run_tests(session, *args)


@nox.session(tags=["test"])
def xdoctest(session: nox.Session) -> None:
    """Run examples with xdoctest."""
    if session.posargs:
        args = [package, *session.posargs]
    else:
        args = [f"--modname={package}", "--command=all"]
        if FORCE_COLOR in os.environ:
            args.append("--colored=1")

    session.install("citric @ .")
    session.install("xdoctest[colors]")
    session.run("python", "-m", "xdoctest", *args)


@nox.session()
def coverage(session: nox.Session) -> None:
    """Upload coverage data."""
    args = session.posargs or ["report"]

    session.install("coverage[toml]")

    if not session.posargs and any(Path().glob(".coverage.*")):
        session.run("coverage", "combine", "--debug=pathmap")

    session.run("coverage", *args)


@nox.session(name="deps", python=python_versions)
def dependencies(session: nox.Session) -> None:
    """Check issues with dependencies."""
    install_env = {}
    if session.python == "3.14":
        install_env["PYO3_USE_ABI3_FORWARD_COMPATIBILITY"] = "1"

    session.install("citric[dev] @ .", env=install_env)
    session.install("deptry")
    session.run("deptry", "src", "tests", "docs")


@nox.session(python=python_versions, tags=["lint"])
def mypy(session: nox.Session) -> None:
    """Type-check using mypy."""
    args = session.posargs or locations
    session.install("citric[typing] @ .")
    session.run("mypy", *args)


@nox.session(name="docs-build")
def docs_build(session: nox.Session) -> None:
    """Build the documentation."""
    args = session.posargs or ["docs", "build"]
    if not session.posargs and FORCE_COLOR in os.environ:
        args.insert(0, "--color")

    session.install("citric[docs] @ .")

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
    session.install("citric[docs] @ .", "sphinx-autobuild")

    build_dir = Path("build")
    if build_dir.exists():
        shutil.rmtree(build_dir)

    session.run("sphinx-autobuild", *args)


@nox.session(name="api")
def api_changes(session: nox.Session) -> None:
    """Check for API changes."""
    args = [
        "griffe",
        "check",
        "citric",
        "-s=src",
    ]

    if GH_ACTIONS_ENV_VAR in os.environ:
        args.append("-f=github")

    if session.posargs:
        args.append(f"-a={session.posargs[0]}")

    session.run(*args, external=True)


@nox.session()
def notebook(session: nox.Session) -> None:
    """Start a Jupyter notebook."""
    session.install(
        "boto3",
        "duckdb",
        "duckdb-engine",
        "faker",
        "jupysql",
        "jupyterlab",
        "pandas",
        "pyarrow",
        "sqlalchemy",
        "-e",
        ".",
    )
    session.run(
        "jupyter",
        "lab",
        env={
            "AWS_ENDPOINT_URL": "http://localhost:9000",
            "AWS_ACCESS_KEY_ID": "minioadmin",
            "AWS_SECRET_ACCESS_KEY": "minioadmin",
        },
    )


@nox.session(name="generate-tags", tags=["status"])
def tags(session: nox.Session) -> None:
    """Print tags."""
    session.install("requests", "requests-cache")
    session.run("python", "scripts/docker_tags.py")

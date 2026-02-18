#!/usr/bin/env -S uv run --script

# /// script
# dependencies = ["nox>=2025.2.9"]
# ///

"""Nox configuration."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import nox

GH_ACTIONS_ENV_VAR = "GITHUB_ACTIONS"
FORCE_COLOR = "FORCE_COLOR"

DOCS_PYTHON = "3.14"  # NOTE: Keep this in sync with .readthedocs.yaml
PYPROJECT = nox.project.load_toml()

nox.needs_version = ">=2025.2.9"
nox.options.default_venv_backend = "uv"
nox.options.reuse_venv = "yes"

package = "citric"

python_versions = nox.project.python_versions(PYPROJECT)

locations = "src", "tests", "docs/conf.py"


@nox.session(python=python_versions, tags=["test"])
@nox.parametrize("constraints", ["highest", "lowest-direct"])
def tests(session: nox.Session, constraints: str) -> None:
    """Execute pytest tests and compute coverage."""
    install_args = [".", "--group=test"]
    if constraints == "lowest-direct":
        install_args.append("--resolution=lowest-direct")

    session.install(*install_args)

    session.run(
        "coverage",
        "run",
        "-m",
        "pytest",
        "-m",
        "not integration_test",
        *session.posargs,
        env={"COVERAGE_CORE": "sysmon"},
    )


@nox.session(tags=["test"])
def integration(session: nox.Session) -> None:
    """Execute integration tests and compute coverage."""
    session.install(".", "--group=test", f"--python={session.virtualenv.location}")
    try:
        session.run(
            "coverage",
            "run",
            "-m",
            "pytest",
            "--integration",
            "-m",
            "integration_test",
            *session.posargs,
            env={"COVERAGE_CORE": "sysmon"},
        )
    finally:
        if session.interactive:
            session.notify("coverage", posargs=[])


@nox.session(tags=["test"])
def xdoctest(session: nox.Session) -> None:
    """Run examples with xdoctest."""
    if session.posargs:
        args = [package, *session.posargs]
    else:
        args = [f"--modname={package}", "--command=all"]
        if FORCE_COLOR in os.environ:
            args.append("--colored=1")

    session.install(".", "--group=test")
    session.run("python", "-m", "xdoctest", *args)


@nox.session(default=False)
def coverage(session: nox.Session) -> None:
    """Upload coverage data."""
    args = session.posargs or ["report"]

    session.install("coverage[toml]")

    if not session.posargs and any(Path().glob(".coverage.*")):
        session.run("coverage", "combine", "--debug=pathmap")

    session.run("coverage", *args)


@nox.session(name="deps", tags=["lint"])
def dependencies(session: nox.Session) -> None:
    """Check issues with dependencies."""
    install_env = {}
    if session.python == "3.15":
        install_env["PYO3_USE_ABI3_FORWARD_COMPATIBILITY"] = "1"

    session.install("citric @ .", env=install_env)
    session.install("deptry")
    session.run("deptry", "src", "tests", "docs")


@nox.session(tags=["lint"])
def mypy(session: nox.Session) -> None:
    """Type-check using mypy."""
    args = session.posargs or [*locations, "noxfile.py"]
    session.install(".", "--group=typing")
    session.run("mypy", *args)


@nox.session(tags=["lint"])
def ty(session: nox.Session) -> None:
    """Type-check using mypy."""
    args = session.posargs or locations
    session.install(".", "--group=typing")
    session.run(
        "ty",
        "check",
        f"--output-format={'github' if os.getenv('GITHUB_ACTIONS') == 'true' else 'concise'}",  # noqa: E501
        *args,
    )


@nox.session(name="docs-build", python=DOCS_PYTHON)
def docs_build(session: nox.Session) -> None:
    """Build the documentation."""
    session.install(".", "-r=requirements/docs.requirements.txt")

    if os.path.exists("build"):  # noqa: PTH110
        shutil.rmtree("build")

    args = ["docs", "build"]
    if not args and FORCE_COLOR in os.environ:
        args.insert(0, "--color")

    session.run(
        "python",
        "-m",
        "sphinx",
        "-T",
        "-W",
        "--keep-going",
        "-b",
        "html",
        "-D",
        "language=en",
        *args,
    )


@nox.session(name="docs-serve", python=DOCS_PYTHON, default=False)
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
    session.install(".", "--group=docs-serve")

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


@nox.session(default=False)
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


if __name__ == "__main__":
    nox.main()

"""Nox configuration."""
import tempfile

import nox
from nox.sessions import Session

# Default sessions
locations = "src", "tests", "noxfile.py", "docs/conf.py"
package = "citric"


def install_with_constraints(session: Session, *args, **kwargs) -> None:
    """Install individual packages with Poetry version constraints."""
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            f"--output={requirements.name}",
            # TODO: remove this
            "--without-hashes",
            external=True,
        )
        session.install(f"--constraint={requirements.name}", *args, **kwargs)


@nox.session(python=["3.10", "3.9", "3.8", "3.7", "3.6"])
def tests(session: Session) -> None:
    """Execute pytest tests."""
    args = session.posargs or ["--cov", "-vvv", "-m", "not integration_test"]
    session.run("poetry", "install", "--no-dev", external=True)
    install_with_constraints(
        session,
        "coverage[toml]",
        "pytest",
        "pytest-cov",
        "psycopg2-binary",
    )
    session.run("pytest", *args)


@nox.session(python=["3.10", "3.9", "3.8"])
def coverage(session: Session) -> None:
    """Upload coverage data."""
    install_with_constraints(session, "coverage[toml]", "codecov")
    session.run("coverage", "xml", "--fail-under=0")
    session.run("codecov", *session.posargs)


@nox.session(python=["3.10", "3.9", "3.8"])
def lint(session: Session) -> None:
    """Check code linting."""
    args = session.posargs or locations
    install_with_constraints(
        session,
        "flake8",
        "flake8-annotations",
        "flake8-black",
        "flake8-docstrings",
        "flake8-isort",
        "darglint",
    )
    session.run("flake8", *args)


@nox.session(python=["3.10", "3.9", "3.8"])
def black(session: Session) -> None:
    """Format code."""
    args = session.posargs or locations
    install_with_constraints(session, "black")
    session.run("black", *args)


@nox.session(python=["3.10", "3.9", "3.8", "3.7", "3.6"])
def mypy(session: Session) -> None:
    """Check types with mypy."""
    args = session.posargs or locations
    session.install(".")
    session.install("mypy", "types-requests")
    session.run("mypy", *args)


@nox.session(python=["3.7", "3.6"])
def pytype(session: Session) -> None:
    """Infer and check types with pytype."""
    args = session.posargs or ["--disable=import-error", *locations]
    install_with_constraints(session, "pytype")
    session.run("pytype", *args)


@nox.session(python=["3.10", "3.9", "3.8", "3.7", "3.6"])
def xdoctest(session: Session) -> None:
    """Run examples with xdoctest."""
    args = session.posargs or ["all"]
    session.run("poetry", "install", "--no-dev", external=True)
    install_with_constraints(session, "xdoctest")
    session.run("python", "-m", "xdoctest", package, *args)


@nox.session(python=["3.10", "3.9", "3.8"])
def docs(session: Session) -> None:
    """Build the documentation."""
    session.run("poetry", "install", "--no-dev", external=True)
    install_with_constraints(
        session,
        "sphinx",
        "sphinx-autodoc-typehints",
        "sphinx-autoapi",
    )
    session.run("sphinx-build", "docs", "docs/_build")


@nox.session(python=["3.10", "3.9", "3.8"])
def safety(session: Session) -> None:
    """Check if packages are safe."""
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            "--without-hashes",
            f"--output={requirements.name}",
            external=True,
        )
        install_with_constraints(session, "safety")
        session.run("safety", "check", f"--file={requirements.name}", "--full-report")

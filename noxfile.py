"""Nox configuration."""
import tempfile

import nox

# Default sessions
locations = "src", "tests", "noxfile.py"


def install_with_constraints(session, *args, **kwargs):
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


@nox.session(python=["3.8", "3.7", "3.6"])
def tests(session):
    """Execute pytest tests."""
    args = session.posargs or ["--cov"]
    session.run("poetry", "install", "--no-dev", external=True)
    install_with_constraints(
        session, "coverage[toml]", "pytest", "pytest-cov", "requests-mock"
    )
    session.run("pytest", *args)


@nox.session(python="3.8")
def coverage(session) -> None:
    """Upload coverage data."""
    install_with_constraints(session, "coverage[toml]", "codecov")
    session.run("coverage", "xml", "--fail-under=0")
    session.run("codecov", *session.posargs)


@nox.session(python=["3.8"])
def lint(session):
    """Check code linting."""
    args = session.posargs or locations
    install_with_constraints(
        session,
        "flake8",
        "flake8-annotations",
        "flake8-black",
        "flake8-docstrings",
        # "flake8-isort",
    )
    session.run("flake8", *args)


@nox.session(python="3.8")
def black(session):
    """Format code."""
    args = session.posargs or locations
    install_with_constraints(session, "black")
    session.run("black", *args)


@nox.session(python=["3.8", "3.7", "3.6"])
def mypy(session):
    """Check types with mypy."""
    args = session.posargs or locations
    install_with_constraints(session, "mypy")
    session.run("mypy", *args)


@nox.session(python=["3.7", "3.6"])
def pytype(session):
    """Infer and check types with pytype."""
    args = session.posargs or ["--disable=import-error", *locations]
    install_with_constraints(session, "pytype")
    session.run("pytype", *args)


@nox.session(python="3.8")
def safety(session):
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

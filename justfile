# Justfile

py := '3.13'

build: update-all test

# Command to update all dependencies
update-all: update-github-actions update-pre-commit-hooks refresh-uv-lock update-lock-files

# Command to update GitHub actions using gha-update
update-github-actions:
    -uvx --python={{py}} gha-update

# Command to update pre-commit hooks
update-pre-commit-hooks:
    -uvx --python={{py}} pre-commit autoupdate

# Command to refresh uv.lock
refresh-uv-lock:
    -uv lock --upgrade

# Update lock files
update-lock-files:
    -uvx --python={{py}} pre-commit run uv-export --all-files
    -uvx --python={{py}} pre-commit run pip-compile --all-files

test: pre-commit nox

# Run pre-commit checks
pre-commit:
    -uvx --python={{py}} pre-commit run --all-files

# Run all nox sessions
nox:
    uvx --python={{py}} nox -r

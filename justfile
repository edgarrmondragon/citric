# Justfile

py := '3.14'

build: update-all test

# Command to update all dependencies
update-all: update-github-actions update-pre-commit-hooks refresh-uv-lock update-lock-files

# Command to update GitHub actions using pinact
update-github-actions:
    -pinact run --update --min-age=7

# Command to update pre-commit hooks
update-pre-commit-hooks:
    -uvx --python={{py}} prek autoupdate --cooldown-days=7

# Command to refresh uv.lock
refresh-uv-lock:
    -uv lock --upgrade

# Update lock files
update-lock-files:
    -uvx --python={{py}} prek run pip-compile --all-files

test: pre-commit nox

# Run pre-commit checks
pre-commit:
    -uvx --python={{py}} prek run --all-files

# Run all nox sessions
nox:
    uvx --python={{py}} nox --reuse-existing-virtualenvs

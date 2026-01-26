# Justfile

build: update-all test

# Command to update all dependencies
update-all: update-github-actions update-pre-commit-hooks

# Command to update GitHub actions using pinact
update-github-actions:
    -pinact run --update --min-age=7

# Command to update pre-commit hooks
update-pre-commit-hooks:
    -uvx prek autoupdate --cooldown-days=7

test: pre-commit nox

# Run pre-commit checks
pre-commit:
    -uvx prek run --all-files

# Run all default nox sessions
nox:
    uvx nox

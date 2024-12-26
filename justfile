# Justfile

default_python := '3.13'

# Command to update all dependencies
update-all py=default_python: (update-github-actions py) (update-pre-commit-hooks py) refresh-uv-lock (update-lock-files py)

# Command to update GitHub actions using gha-update
update-github-actions py=default_python:
    -uvx --python={{py}} gha-update

# Command to update pre-commit hooks
update-pre-commit-hooks py=default_python:
    -uvx --python={{py}} pre-commit autoupdate

# Command to refresh uv.lock
refresh-uv-lock:
    -uv lock --upgrade

# Update lock files
update-lock-files py=default_python:
    -uvx --python={{py}} pre-commit run uv-export --all-files
    -uvx --python={{py}} pre-commit run pip-compile --all-files

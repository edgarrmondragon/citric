# Justfile

build: update test clean

# Command to update all dependencies
update: update-github-actions update-docs update-pre-commit-hooks update-tags

# Command to update GitHub actions using pinact
update-github-actions:
    -pinact run --update --min-age=7

# Command to update pre-commit hooks
update-pre-commit-hooks:
    -uvx prek autoupdate --cooldown-days=7

# Update Docker tags
update-tags:
    ./scripts/docker_tags.py

# Update docs requirements
update-docs:
    rm requirements/docs.requirements.txt
    uv pip compile pyproject.toml --group=docs --python-version=3.14 --output-file=requirements/docs.requirements.txt

# Serve docs
docs-serve:
    ./noxfile.py -s docs-serve

test: pre-commit lint nox

# Run pre-commit checks
pre-commit:
    -uvx prek run --all-files

# Lint
lint:
    ./noxfile.py -t lint

# Run all default nox sessions
nox:
    -./noxfile.py -s

# Clean build artifacts, coverage files, and nox venvs
clean:
    rm -rf build .coverage.* .nox/
    find . -type d -name '__pycache__' -exec rm -r {} +

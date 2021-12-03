# Citric

[![Documentation Status][docs-badge]][docs-link]
[![Updates][updates-badge]][updates-link]
[![codecov][codecov-badge]][codecov-link]
[![PyPI version][pypi-badge]][pypi-link]
[![Python versions][versions-badge]][pypi-link]
[![Tests][tests-badge]][tests-link]
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fedgarrmondragon%2Fcitric.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2Fedgarrmondragon%2Fcitric?ref=badge_shield)

A client to the LimeSurvey Remote Control API 2, written in modern
Python.

## Features

### Low-level JSON-RPC API

For the full reference, see the [RemoteControl 2 API docs][rc2api].

```python
from citric import Client

LS_URL = "http://localhost:8001/index.php/admin/remotecontrol"

with Client(LS_URL, "iamadmin", "secret") as client:
    # Get all surveys from user "iamadmin"
    surveys = client.list_surveys("iamadmin")

    for s in surveys:
        print(s["surveyls_title"])

        # Get all questions, regardless of group
        questions = client.list_questions(s["sid"])
        for q in questions:
            print(q["title"], q["question"])
```

## Development

Use pyenv to setup default Python versions for this repo:

```shell
pyenv local 3.10.0 3.9.7 3.8.11 3.7.11 3.6.14
```

Install project dependencies

```shell
poetry install
```

### Docker

You can setup a local instance of LimeSurvey with [Docker Compose](https://docs.docker.com/compose/):

```shell
docker-compose up -d
```

Now you can access LimeSurvey at [port 8001](http://localhost:8001/index.php/admin).

Import an existing survey file and start testing with it:

```python
from citric import Client

LS_URL = "http://localhost:8001/index.php/admin/remotecontrol"
SURVEY_FILE = "examples/limesurvey_survey_432535.lss"

with Client(LS_URL, "iamadmin", "secret") as client:
    # Import survey from a file
    survey_id = client.import_survey(SURVEY_FILE, "lss")
    print("New survey:", survey_id)
```

### Testing

This project uses [`nox`][nox] for running tests and linting on different Python versions:

```shell
pip install --user --upgrade nox
nox -r
```

Run only a linting session

```shell
nox -rs lint
```

### pre-commit

```shell
pip install --user --upgrade pre-commit
pre-commit install
```

### Releasing an upgrade

Bump the package version

```shell
poetry version <version>
poetry publish
```

## Credits

- [Claudio Jolowicz][claudio] and [his amazing blog post][hypermodern].

[rc2api]: https://api.limesurvey.org/classes/remotecontrol_handle.html
[nox]: https://nox.thea.codes/en/stable/
[claudio]: https://twitter.com/cjolowicz/
[hypermodern]: https://cjolowicz.github.io/posts/hypermodern-python-01-setup/

<!--Badges-->
[docs-badge]: https://readthedocs.org/projects/citric/badge/?version=latest
[docs-link]: https://citric.readthedocs.io/en/latest/?badge=latest
[updates-badge]: https://pyup.io/repos/github/edgarrmondragon/citric/shield.svg
[updates-link]: https://pyup.io/repos/github/edgarrmondragon/citric/
[codecov-badge]: https://codecov.io/gh/edgarrmondragon/citric/branch/master/graph/badge.svg
[codecov-link]: https://codecov.io/gh/edgarrmondragon/citric
[tests-badge]: https://github.com/edgarrmondragon/citric/workflows/Tests/badge.svg
[tests-link]: https://github.com/edgarrmondragon/citric/actions?workflow=Tests
[pypi-badge]: https://img.shields.io/pypi/v/citric.svg
[versions-badge]: https://img.shields.io/pypi/pyversions/citric.svg
[pypi-link]: https://pypi.org/project/citric


## License
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fedgarrmondragon%2Fcitric.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Fedgarrmondragon%2Fcitric?ref=badge_large)
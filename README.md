# Citric

[![Documentation Status][docs-badge]][docs-link]
[![Updates][updates-badge]][updates-link]
[![codecov][codecov-badge]][codecov-link]
[![Tests][tests-badge]][tests-link]

A client to the LimeSurvey Remote Control API 2, written in modern
Python.

## Features

### Low-level JSON-RPC API

For the full reference, see the [RemoteControl 2 API docs][rc2api].

```python
from citric.rpc import Session

LS_URL = 'http://my-ls-server.com/index.php/admin/remotecontrol'

with Session(LS_URL, 'iamadmin', 'secret') as session:
   # Get all surveys from user 'iamadmin'
   r = session.rpc('list_surveys', 'iamadmin')

   if r.error is None:
      surveys = r.result
      for s in surveys:
         print(s["surveyls_title"])

         # Get all questions, regardless of group
         r = session.rpc("list_questions", s["sid"])
         questions = r.result
         for q in questions:
            print(q["title"], q["question"])
```

## Development

Use pyenv to setup default Python versions for this repo:

```shell
pyenv local 3.8.3 3.7.7 3.6.10
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

Now you can access LimeSurvey at [port 8001](http://localhost:8001/index).php/admin.

Import an existing survey file and start testing with it:

```python
import base64

from citric.rpc import Session

LS_URL = "http://localhost:8001/index.php/admin/remotecontrol"
SURVEY_FILE = "examples/limesurvey_survey_432535.lss"

with Session(LS_URL, "iamadmin", "secret") as session, open(SURVEY_FILE, "rb") as file:
    # Import survey from file
    contents = file.read()

    string = base64.b64encode(contents).decode()
    r = session.rpc("import_survey", string, "lss")

    if r.error is None:
      survey_id = r.result
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

[rc2api]: https://api.limesurvey.org/classes/remotecontrol_handle.html
[nox]: https://nox.thea.codes/en/stable/

<!--Badges-->
[docs-badge]: https://readthedocs.org/projects/citric/badge/?version=latest
[docs-link]: https://citric.readthedocs.io/en/latest/?badge=latest
[updates-badge]: https://pyup.io/repos/github/edgarrmondragon/citric/shield.svg
[updates-link]: https://pyup.io/repos/github/edgarrmondragon/citric/
[codecov-badge]: https://codecov.io/gh/edgarrmondragon/citric/branch/master/graph/badge.svg
[codecov-link]: https://codecov.io/gh/edgarrmondragon/citric
[tests-badge]: https://github.com/edgarrmondragon/citric/workflows/Tests/badge.svg
[tests-link]: https://github.com/edgarrmondragon/citric/actions?workflow=Tests

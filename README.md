# Citric

[![Tests][tests-badge]][tests-link]
[![Documentation Status][docs-badge]][docs-link]
[![Updates][updates-badge]][updates-link]
[![codecov][codecov-badge]][codecov-link]
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fedgarrmondragon%2Fcitric.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2Fedgarrmondragon%2Fcitric?ref=badge_shield)
[![PyPI version][pypi-badge]][pypi-link]
[![Python versions][versions-badge]][pypi-link]
[![PyPI - Downloads][downloads-badge]][pypi-link]

A client to the LimeSurvey Remote Control API 2, written in modern
Python.

## Installation

```console
$ pip install citric
```

## Usage

For the full JSON-RPC reference, see the [RemoteControl 2 API docs][rc2api].

### Get surveys and questions

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

### Export responses to a `pandas` dataframe

```python
import io
import pandas as pd

survey_id = 123456

df = pd.read_csv(
    io.BytesIO(client.export_responses(survey_id, file_format="csv")),
    delimiter=";",
    parse_dates=["datestamp", "startdate", "submitdate"],
    index_col="id",
)
```

### Custom `requests` session

It's possible to use a custom session object to make requests. For example, to cache the requests
and reduce the load on your server in read-intensive applications, you can use
[`requests-cache`](https://requests-cache.readthedocs.io):

```python
import requests_cache

cached_session = requests_cache.CachedSession(
    expire_after=3600,
    allowable_methods=["POST"],
)

with Client(
    LS_URL,
    "iamadmin",
    "secret",
    requests_session=cached_session,
) as client:

    # Get all surveys from user "iamadmin"
    surveys = client.list_surveys("iamadmin")

    # This should hit the cache. Running the method in a new client context will
    # not hit the cache because the RPC session key would be different.
    surveys = client.list_surveys("iamadmin")
```

### Use a different authentication plugin

By default, this client uses the internal database for authentication but
[arbitrary plugins](https://manual.limesurvey.org/Authentication_plugins) are supported by the
`auth_plugin` argument.

```python
with Client(
    LS_URL,
    "iamadmin",
    "secret",
    auth_plugin="AuthLDAP",
) as client:
    ...
```

Common plugins are `Authdb` (default), `AuthLDAP` and `Authwebserver`.

### Get uploaded files and move them to S3

```python
import base64
import io

import boto3
from citric import Client

s3 = boto3.client("s3")

with Client(
    "https://mylimeserver.com/index.php/admin/remotecontrol",
    "iamadmin",
    "secret",
) as client:
    survey_id = 12345
    files = client.get_uploaded_files(survey_id)
    for file in files:
        content = base64.b64decode(files[file]["content"])  # Decode content
        question_id = files[file]["meta"]["question"]["qid"]
        s3.upload_fileobj(
            io.BytesIO(content),
            "my-s3-bucket",
            f"uploads/{survey_id}/{question_id}/{file}",
        )
```

### Fall back to `citric.Session` for low-level interaction

This library doesn't (yet) implement all RPC methods, so if you're in dire need to use a method not currently supported, you can use the `session` attribute to invoke the underlying RPC interface without having to pass a session key explicitly:

```python
# Call the copy_survey method, not available in Client
with Client(LS_URL, "iamadmin", "secret") as client:
    new_survey_id = client.session.copy_survey(35239, "copied_survey")
```

### Notebook samples

- [Import a survey file from S3](https://github.com/edgarrmondragon/citric/blob/master/docs/notebooks/import_s3.ipynb)
- [Download responses and save them to a SQLite database](https://github.com/edgarrmondragon/citric/blob/master/docs/notebooks/pandas_sqlite.ipynb)

## Development

Use pyenv to setup default Python versions for this repo:

```shell
pyenv local 3.10.0 3.9.7 3.8.11 3.7.11
```

Install project dependencies

```shell
poetry install
```

### Docs

To generate the documentation site, use the following commands:

```shell
poetry install -E docs
poetry run sphinx-build docs build
```

### Docker

You can setup a local instance of LimeSurvey with [Docker Compose](https://docs.docker.com/compose/):

```shell
docker compose -f docker-compose.yml -f docker-compose.test.yml up -d
```

Now you can access LimeSurvey at [port 8001](http://localhost:8001/index.php/admin).

Import an existing survey file and start testing with it:

```python
from citric import Client

LS_URL = "http://localhost:8001/index.php/admin/remotecontrol"

with Client(LS_URL, "iamadmin", "secret") as client:
    # Import survey from a file
    with open("examples/limesurvey_survey_432535.lss", "rb") as f:
        survey_id = client.import_survey(f, "lss")
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

1. Update the changelog

   ```shell
   changie batch <version>
   changie merge
   ```

1. Bump the package version

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
[pypi-badge]: https://img.shields.io/pypi/v/citric.svg?color=blue
[versions-badge]: https://img.shields.io/pypi/pyversions/citric.svg
[downloads-badge]: https://img.shields.io/pypi/dm/citric?color=blue
[pypi-link]: https://pypi.org/project/citric


## License
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fedgarrmondragon%2Fcitric.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Fedgarrmondragon%2Fcitric?ref=badge_large)

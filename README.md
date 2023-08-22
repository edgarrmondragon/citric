<div align="center">

# Citric

<div>
  <a href="https://github.com/edgarrmondragon/citric/blob/main/LICENSE">
    <img alt="License" src="https://img.shields.io/github/license/edgarrmondragon/citric"/>
  </a>
  <a href="https://github.com/astral-sh/ruff">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json" alt="Ruff" style="max-width:100%;">
  </a>
  <a href="https://github.com/wntrblm/nox">
    <img alt="Nox" src="https://img.shields.io/badge/%F0%9F%A6%8A-Nox-D85E00.svg"/>
  </a>
  <a href="https://python-poetry.org/">
    <img alt="Poetry" src="https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json"/>
  </a>
</div>

<div>
  <a href="https://results.pre-commit.ci/latest/github/edgarrmondragon/citric/main">
    <img alt="pre-commit.ci status" src="https://results.pre-commit.ci/badge/github/edgarrmondragon/citric/main.svg"/>
  </a>
  <a href="https://citric.readthedocs.io/en/latest/?badge=latest">
    <img alt="Documentation Status" src="https://readthedocs.org/projects/citric/badge/?version=latest"/>
  </a>
  <a href="https://codecov.io/gh/edgarrmondragon/citric">
    <img alt="codecov" src="https://codecov.io/gh/edgarrmondragon/citric/branch/main/graph/badge.svg"/>
  </a>
  <a href="https://app.fossa.com/projects/git%2Bgithub.com%2Fedgarrmondragon%2Fcitric?ref=badge_shield">
    <img alt="FOSSA Status" src="https://app.fossa.com/api/projects/git%2Bgithub.com%2Fedgarrmondragon%2Fcitric.svg?type=shield"/>
  </a>
</div>

<div>
  <a href="https://pypi.org/project/citric">
    <img alt="PyPI version" src="https://img.shields.io/pypi/v/citric.svg?color=blue"/>
  </a>
  <a href="https://pypi.org/project/citric">
    <img alt="Python versions" src="https://img.shields.io/pypi/pyversions/citric.svg"/>
  </a>
  <a href="https://pypi.org/project/citric">
    <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/citric?color=blue"/>
  </a>
</div>

A client to the [LimeSurvey Remote Control API 2](https://manual.limesurvey.org/RemoteControl_2_API), written in modern
Python.
</div>

## Features

- Supports the full RPC API via the [`Session` class](https://citric.readthedocs.io/en/latest/_api/citric/session/index.html#citric.session.Session).
- Best effort to implement all the RPC methods in the [`Client` class](https://citric.readthedocs.io/en/stable/_api/citric/index.html#citric.Client). See the [API coverage page](https://citric.readthedocs.io/en/stable/rpc_coverage.html) for details.
- Easily export survey data to CSV files, [Pandas DataFrames](https://citric.readthedocs.io/en/stable/how-to.html#export-responses-to-a-pandas-dataframe) and [DuckDB databases](https://citric.readthedocs.io/en/stable/how-to.html#export-responses-to-a-duckdb-database-and-analyze-with-sql).
- Easily [download survey files](https://citric.readthedocs.io/en/stable/how-to.html#get-files-uploaded-to-a-survey-and-move-them-to-s3) (e.g. images, audio, etc.) to a local directory.
- Tested against LimeSurvey 6.0.0+ and 5.0.0+ LTS versions.

### Integration tests

| LimeSurvey version | Database   | Status |
| -------------------| ---------- | ------ |
| Latest 6           | PostgreSQL | ![Status of 6+ integration tests, postgres](https://img.shields.io/endpoint?url=https%3A%2F%2Fgist.githubusercontent.com%2Fedgarrmondragon%2F02f3c72747cc609788c75c3cd32b4e97%2Fraw%2Fbadge-integration-3.11-6-apache-postgres.json) |
| Latest 6           | MySQL      | ![Status of 6+ integration tests, mysql](https://img.shields.io/endpoint?url=https%3A%2F%2Fgist.githubusercontent.com%2Fedgarrmondragon%2F02f3c72747cc609788c75c3cd32b4e97%2Fraw%2Fbadge-integration-3.11-6-apache-mysql.json) |
| 6.2.1+230807       | PostgreSQL | ![Status of 6.2.1+230807 integration tests, postgres](https://img.shields.io/endpoint?url=https%3A%2F%2Fgist.githubusercontent.com%2Fedgarrmondragon%2F02f3c72747cc609788c75c3cd32b4e97%2Fraw%2Fbadge-integration-3.11-6.2.1-230807-apache-postgres.json) |
| 6.2.2+230814       | PostgreSQL | ![Status of 6.2.2+230814 integration tests, postgres](https://img.shields.io/endpoint?url=https%3A%2F%2Fgist.githubusercontent.com%2Fedgarrmondragon%2F02f3c72747cc609788c75c3cd32b4e97%2Fraw%2Fbadge-integration-3.11-6.2.2-230814-apache-postgres.json) |
| Latest 5           | PostgreSQL | ![Status of 5+ integration tests, postgres](https://img.shields.io/endpoint?url=https%3A%2F%2Fgist.githubusercontent.com%2Fedgarrmondragon%2F02f3c72747cc609788c75c3cd32b4e97%2Fraw%2Fbadge-integration-3.11-5-apache-postgres.json) |
| 5.6.34+230816      | PostgreSQL | ![Status of 5.6.34-230816 integration tests, postgres](https://img.shields.io/endpoint?url=https%3A%2F%2Fgist.githubusercontent.com%2Fedgarrmondragon%2F02f3c72747cc609788c75c3cd32b4e97%2Fraw%2Fbadge-integration-3.11-5.6.34-230816-apache-postgres.json) |
| `master` branch    | PostgreSQL | ![Status of master branch integration tests, postgres](https://img.shields.io/endpoint?url=https%3A%2F%2Fgist.githubusercontent.com%2Fedgarrmondragon%2F02f3c72747cc609788c75c3cd32b4e97%2Fraw%2Fbadge-integration-3.11-master-postgres.json) |
| `develop` branch   | PostgreSQL | ![Status of develop branch integration tests, postgres](https://img.shields.io/endpoint?url=https%3A%2F%2Fgist.githubusercontent.com%2Fedgarrmondragon%2F02f3c72747cc609788c75c3cd32b4e97%2Fraw%2Fbadge-integration-3.11-develop-postgres.json) |
| `5.x` branch       | PostgreSQL | ![Status of 5.x branch integration tests, postgres](https://img.shields.io/endpoint?url=https%3A%2F%2Fgist.githubusercontent.com%2Fedgarrmondragon%2F02f3c72747cc609788c75c3cd32b4e97%2Fraw%2Fbadge-integration-3.11-5.x-postgres.json) |

## Installation

```console
$ pip install citric
```

## Usage

```python
from citric import Client

with Client(
    "https://mylimesite.limequery.com/admin/remotecontrol",
    "myusername",
    "mypassword",
) as client:
    for survey in client.list_surveys():
        print(survey["surveyls_title"])
```

## Documentation

Code samples and API documentation are available at [citric.readthedocs.io](https://citric.readthedocs.io/).

## Contributing

If you'd like to contribute to this project, please see the [contributing guide](https://citric.readthedocs.io/en/stable/contributing/getting-started.html).

## Credits

- [Claudio Jolowicz][claudio] and [his amazing blog post][hypermodern].

[claudio]: https://twitter.com/cjolowicz/
[hypermodern]: https://cjolowicz.github.io/posts/hypermodern-python-01-setup/

## License
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fedgarrmondragon%2Fcitric.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Fedgarrmondragon%2Fcitric?ref=badge_large)

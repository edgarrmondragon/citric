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
  <a href="https://www.bestpractices.dev/projects/8144">
    <img src="https://www.bestpractices.dev/projects/8144/badge">
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
  <a href="https://zenodo.org/doi/10.5281/zenodo.10216279">
    <img src="https://zenodo.org/badge/223537606.svg" alt="DOI">
  </a>
</div>

<div>
  <a href="https://pypi.org/project/citric">
    <img alt="PyPI version" src="https://img.shields.io/pypi/v/citric.svg?logo=pypi&logoColor=FFE873&color=blue"/>
  </a>
  <a href="https://pypi.org/project/citric">
    <img alt="Python versions" src="https://img.shields.io/pypi/pyversions/citric.svg?logo=python&logoColor=FFE873"/>
  </a>
  <a href="https://pypi.org/project/citric">
    <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/citric?color=blue"/>
  </a>
</div>

*A client to the [LimeSurvey Remote Control API 2](https://manual.limesurvey.org/RemoteControl_2_API), written in modern Python.*

</div>

<!-- begin-short -->

## Features

- Supports the full RPC API via the [`Session` class](https://citric.readthedocs.io/en/latest/_api/citric/session/index.html#citric.session.Session).
- Best effort to implement all the RPC methods in the [`Client` class](https://citric.readthedocs.io/en/stable/_api/citric/index.html#citric.Client). See the [API coverage page](https://citric.readthedocs.io/en/stable/rpc_coverage.html) for details.
- Easily export survey data to CSV files, [Pandas DataFrames](https://citric.readthedocs.io/en/stable/how-to.html#export-responses-to-a-pandas-dataframe) and [DuckDB databases](https://citric.readthedocs.io/en/stable/how-to.html#export-responses-to-a-duckdb-database-and-analyze-with-sql).
- Easily [download survey files](https://citric.readthedocs.io/en/stable/how-to.html#get-files-uploaded-to-a-survey-and-move-them-to-s3) (e.g. images, audio, etc.) to a local directory.
- Tested against LimeSurvey 6.0.0+ and 5.0.0+ versions.
- Experimental support for the new [REST API](https://manual.limesurvey.org/REST_API).

### Integration tests

Integration tests are run against a LimeSurvey instance, and both PostgreSQL and MySQL backends, using Docker Compose. The following versions of LimeSurvey were tested for this release:

- [6.3.7](https://github.com/LimeSurvey/LimeSurvey/releases/tag/6.3.7%2B231127)
- [6.3.6](https://github.com/LimeSurvey/LimeSurvey/releases/tag/6.3.6%2B231120)
- [6.3.5](https://github.com/LimeSurvey/LimeSurvey/releases/tag/6.3.5%2B231113)
- [5.6.47](https://github.com/LimeSurvey/LimeSurvey/releases/tag/5.6.47%2B231128)
- [5.6.46](https://github.com/LimeSurvey/LimeSurvey/releases/tag/5.6.46%2B231121)
- [5.6.45](https://github.com/LimeSurvey/LimeSurvey/releases/tag/5.6.45%2B231114)

## Installation

```console
$ pip install citric
```

## Usage

```python
from citric import Client

# Connect to your LimeSurvey instance
client =  Client(
    "https://mylimesite.limequery.com/admin/remotecontrol",
    "myusername",
    "mypassword",
)

# Print the LimeSurvey version
print(client.get_server_version())

# Print every survey's title
for survey in client.list_surveys():
    print(survey["surveyls_title"])
```

<!-- end-short -->

## Documentation

Code samples and API documentation are available at [citric.readthedocs.io](https://citric.readthedocs.io/).

## Contributing

If you'd like to contribute to this project, please see the [contributing guide](https://citric.readthedocs.io/en/stable/contributing/getting-started.html).

## Credits

- [Markus Opolka][martialblog] for maintaining a very robust set of [LimeSurvey Docker images](https://github.com/martialblog/docker-limesurvey/).
- [Claudio Jolowicz][claudio] and [his amazing blog post][hypermodern].

[claudio]: https://twitter.com/cjolowicz/
[hypermodern]: https://cjolowicz.github.io/posts/hypermodern-python-01-setup/
[martialblog]: https://github.com/martialblog/

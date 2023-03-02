<div align="center">

# Citric

<div>
  <a href="https://github.com/edgarrmondragon/citric/actions?workflow=Tests">
    <img alt="Tests" src="https://github.com/edgarrmondragon/citric/workflows/Tests/badge.svg"/>
  </a>
  <a href="https://results.pre-commit.ci/latest/github/edgarrmondragon/citric/main">
    <img alt="pre-commit.ci status" src="https://results.pre-commit.ci/badge/github/edgarrmondragon/citric/main.svg"/>
  </a>
  <a href="https://github.com/edgarrmondragon/citric/blob/main/LICENSE">
    <img alt="License" src="https://img.shields.io/github/license/edgarrmondragon/citric"/>
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
  <a href="https://pypi.org/project/citric">
    <img alt="PyPI - Format" src="https://img.shields.io/pypi/format/citric"/>
  </a>
</div>

<div>
  <a href="https://github.com/edgarrmondragon/citric/search?l=python">
    <img alt="GitHub languages" src="https://img.shields.io/github/languages/top/edgarrmondragon/citric">
  </a>
  <img alt="GitHub repo size" src="https://img.shields.io/github/repo-size/edgarrmondragon/citric">
  <a href="https://github.com/edgarrmondragon/citric/stargazers">
    <img alt="GitHub stars" src="https://img.shields.io/github/stars/edgarrmondragon/citric">
  </a>
  <a href="https://github.com/edgarrmondragon/citric/commits/main">
    <img alt="Github last-commit" src="https://img.shields.io/github/last-commit/edgarrmondragon/citric"/>
  </a>
</div>

A client to the [LimeSurvey Remote Control API 2](https://manual.limesurvey.org/RemoteControl_2_API), written in modern
Python.
</div>

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

If you'd like to contribute to this project, please see the [contributing guide](https://citric.readthedocs.io/en/latest/contributing/getting-started.html).

## Credits

- [Claudio Jolowicz][claudio] and [his amazing blog post][hypermodern].

[claudio]: https://twitter.com/cjolowicz/
[hypermodern]: https://cjolowicz.github.io/posts/hypermodern-python-01-setup/

## License
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fedgarrmondragon%2Fcitric.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Fedgarrmondragon%2Fcitric?ref=badge_large)

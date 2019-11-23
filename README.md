# Limette

[//]: # (Badges)
[![PyPI](https://img.shields.io/pypi/v/limette.svg)][pypi]
[![Travis builds](https://img.shields.io/travis/mrfunnyshoes/limette.svg)][travis]
[![Documentation Status](https://readthedocs.org/projects/limette/badge/?version=latest)][docs]
[![Updates](https://pyup.io/repos/github/mrfunnyshoes/limette/shield.svg)][pyup]

A client to the LimeSurvey Remote Control API 2, written in modern Python.

## Features

### Low-level JSON-RPC API

```python
from limette.rpc import Session

with Session('http://my-ls-server.com', 'iamadmin', 'secret') as session:
    response = session.rpc('list_surveys', 'iamadmin')
    surveys = response.result
```

## Testing

This project uses [`tox`](https://tox.readthedocs.io/en/latest/) for runinng tests on different Python versions:

```bash
tox
```

## Credits

This package was created with [Cookiecutter] and the [audreyr/cookiecutter-pypackage] project template.

[pypi]: https://pypi.python.org/pypi/limette
[travis]: https://travis-ci.org/mrfunnyshoes/limette
[docs]: https://limette.readthedocs.io/en/latest/?badge=latest
[pyup]: https://pyup.io/repos/github/mrfunnyshoes/limette/

[Cookiecutter]: https://github.com/audreyr/cookiecutter
[audreyr/cookiecutter-pypackage]: https://github.com/audreyr/cookiecutter-pypackage

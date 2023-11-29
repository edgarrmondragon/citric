# Testing

After you've [set up your environment][environment], you can run tests on Python 3.10:

```shell
nox -rs tests -p "3.10"
```

## Coverage

I strive to maintain 100% _combined_ coverage (from multiple Python versions, as well
as integration tests), so make sure your changes are tested. To run integration tests,
you can follow the [Docker guide][docker].

## Other tests

### Doctests

```shell
nox -rs xdoctest -p 3.12
```

### Type checking

```shell
nox -rs mypy -p 3.12
```

### Dependency checks

```shell
nox -rs deps -p 3.12
```

[environment]: /contributing/environment
[docker]: /contributing/docker

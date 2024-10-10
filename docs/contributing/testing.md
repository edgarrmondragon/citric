# Testing

After you've [set up your environment][environment], you can run tests on available Python interpreters:

```shell
nox -rs tests
```

## Coverage

I strive to maintain 100% _combined_ coverage (from multiple Python versions, as well
as integration tests), so make sure your changes are tested. To run integration tests,
you can follow the [Docker guide][docker].

## Other tests

### Doctests

```shell
nox -rs xdoctest
```

### Type checking

```shell
nox -rs mypy
```

### Dependency checks

```shell
nox -rs deps
```

[docker]: /contributing/docker
[environment]: /contributing/environment

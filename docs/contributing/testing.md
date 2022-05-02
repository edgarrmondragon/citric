# Testing

After you've [set up your environment][environment], you can run tests on Python 3.10:

```shell
nox -rs tests -p "3.10"
```

## Coverage

I strive to maintain 100% _combined_ coverage (from multiple Python versions, as well
as integration tests), so make sure your changes are tested. To run integration tests,
you can follow the [Docker guide][docker].

[environment]: /contributing/environment
[docker]: /contributing/docker

# Testing

After you've [set up your environment][environment], you can run tests on available Python interpreters:

```shell
nox -s tests
```

## Integration tests

<!-- Explain that the integration tests need the Docker daemon running and the Docker CLI available. -->

To run integration tests, the [Docker] daemon must be running and the Docker CLI must be available.

```shell
nox -s integration
```

You can customize the following settings:

| pytest option | Environment variable | Description |
| :---------------------------- | :------------------- | :---------------------------------------------- |
| `--limesurvey-database-type` | `LS_DATABASE_TYPE` | Database used for integration tests |
| `--limesurvey-image-tag` | `LS_IMAGE_TAG` | Docker image tag for integration tests |
| `--limesurvey-username` | `LS_USER` | Username of the LimeSurvey user to test against |
| `--limesurvey-password` | `LS_PASSWORD` | Password of the LimeSurvey user to test against |
| `--limesurvey-password` | `LS_PASSWORD` | Password of the LimeSurvey user to test against |
| `--limesurvey-git-reference` | `LS_REF` | Reference to a specific LimeSurvey commit |
| `--limesurvey-docker-context` | `LS_DOCKER_CONTEXT` | Path to the directory containing the Dockerfile |

The easiest way to set these is to create a `.env` file in the root of the repository.

For example, to test against [the `6.6.4-240923-apache` image][6.6.4] with a MySQL database:

```shell
LS_DATABASE_TYPE=mysql
LS_IMAGE_TAG=6.6.4-240923-apache
```

Or to test against the `master` branch:

```shell
LS_REF=refs/heads/master
```

Or to test against a specific commit (e.g. `f148781ec57fd1a02e5faa26a7465d78c9ab5dfe`):

such a version in CI, add the following to the test matrix in the `integration` job:

```shell
LS_REF=f148781ec57fd1a02e5faa26a7465d78c9ab5dfe
```

## Coverage

I strive to maintain 100% _combined_ coverage (from multiple Python versions, as well
as integration tests), so make sure your changes are tested..

## Other tests

### Doctests

```shell
nox -s xdoctest
```

### Type checking

```shell
nox -s mypy
```

### Dependency checks

```shell
nox -s deps
```

[6.6.4]: https://hub.docker.com/layers/martialblog/limesurvey/6.6.4-240923-apache/images/sha256-4f5ebdd7ee321e4acd828e3800e7546d4bcabb5024c76f87e23a4bd85622e30e
[docker]: https://docs.docker.com/get-started/get-docker/
[environment]: /contributing/environment

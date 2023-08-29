# Docker

You can setup a local instance of LimeSurvey with
[Docker Compose](https://docs.docker.com/compose/):

```shell
docker compose up -d
```

Now you can access LimeSurvey at [port 8001](http://localhost:8001/index.php/admin).

## Other LimeSurvey versions

By default, citric is tested against the latest `6-apache` tag of LimeSurvey.
If you want to use [a different tag](https://hub.docker.com/r/martialblog/limesurvey/tags),
you can specify it using the `LS_IMAGE_TAG` environment variable.

```shell
export LS_IMAGE_TAG=6.0.7+230515-apache
docker compose up -d
```

## Integration tests

Docker Compose allows you to run integration tests against a local instance of
LimeSurvey. First you'll need to setup the environment variables:

```shell
export BACKEND=postgres
export LS_URL=http://localhost:8001/index.php/admin/remotecontrol
export LS_USER=iamadmin
export LS_PASSWORD=secret
```

Then you can run the tests with Nox:

```shell
nox -rs integration
```

```{tip}
You can use the `--force-python` option to run the tests on a different
Python version from the default one (`3.11`).
```

### Run integration tests on a specific LimeSurvey version

```shell
export LS_IMAGE_TAG='6.0.7+230515-apache'

docker-compose -d

nox -rs integration
```

### Run integration tests against an unreleased LimeSurvey version

```shell
export DOCKER_BUILDKIT=0
export LS_VERSION=f148781ec57fd1a02e5faa26a7465d78c9ab5dfe
export LS_CHECKSUM=64aec410738b55c51045ac15373e2bc376e67cd6e20938d759c4596837ef6154

docker compose \
    -f docker-compose.yml \
    -f docker-compose.ref.yml up \
    -d

nox -rs integration
```

Where `LS_VERSION` is the commit SHA at the point of interest and `LS_CHECKSUM`
is the SHA256 checksum of the `.tar.gz` archive of the project at that commit.

````{tip}
You can obtain the checksum by running:

```shell
wget https://github.com/LimeSurvey/LimeSurvey/archive/${LS_VERSION}.tar.gz
sha256sum ${LS_VERSION}.tar.gz
```
````

To test against such a version in CI, add the following to the job matrix:

```yaml
- python-version: "3.11"
  os: "ubuntu-latest"
  session: "integration"
  limesurvey_version: "f148781ec57fd1a02e5faa26a7465d78c9ab5dfe"
  database: postgres
  experimental: true
```

# Docker

You can setup a local instance of LimeSurvey with
[Docker Compose](https://docs.docker.com/compose/):

```shell
docker compose up -d
```

Now you can access LimeSurvey at [port 8001](http://localhost:8001/index.php/admin).

## Other LimeSurvey versions

By default, citric is tested against the latest `5-apache` tag of LimeSurvey.
If you want to use [a different tag](https://hub.docker.com/r/martialblog/limesurvey/tags),
you can specify it using the `LS_IMAGE_TAG` environment variable.

```shell
export LS_IMAGE_TAG=5.3.10-220419-apache
docker compose up -d
```

## Integration tests

Integrations tests rely on LimeSurver's PostgreSQL database being exposed to the
host, so you'll need to override the `db` service with the definition in
`docker-compose.test.yml`:

```shell
docker-compose -d
```

Now you can run the tests mark as `integration_test`:

```shell
nox -rs tests --python "3.10" -- -m "integration_test"
```

### Run integraton tests on a specific LimeSurvey version

```shell
export LS_IMAGE_TAG='5.3.10-220419-apache'

docker-compose -d

nox -rs tests --python "3.10" -- -m "integration_test"
```

### Run integraton tests on unreleased LimeSurvey version

```shell
export DOCKER_BUILDKIT=0
export LS_VERSION=5af7b00a674ecb872cd2f359366946f572af69b0
export LS_CHECKSUM=f21777810430c533929f51f5999e2b3bed0fc9c9921a461f21376b83a45fad9b

docker-compose \
    -f docker-compose.yml \
    -f docker-compose.ref.yml up \
    -d

nox -rs tests --python "3.10" -- -m "integration_test"
```

Where `LS_VERSION` is the commit SHA at the point of interest, while `LS_CHECKSUM`
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
- python-version: "3.10"
  os: "ubuntu-latest"
  session: "integration"
  experimental: false
  limesurvey_version: 5af7b00a674ecb872cd2f359366946f572af69b0
  limesurvey_checksum: f21777810430c533929f51f5999e2b3bed0fc9c9921a461f21376b83a45fad9b
```

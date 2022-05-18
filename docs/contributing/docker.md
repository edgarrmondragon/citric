# Docker

You can setup a local instance of LimeSurvey with
[Docker Compose](https://docs.docker.com/compose/):

```shell
docker compose -f docker-compose.yml -f docker-compose.test.yml up -d
```

Now you can access LimeSurvey at [port 8001](http://localhost:8001/index.php/admin).

## Other LimeSurvey versions

By default, citric is tested against the latest `5-apache` tag of LimeSurvey.
If you want to use [a different tag](https://hub.docker.com/r/meltano/meltano/tags),
you can specify it using the `LS_IMAGE_TAG` environment variable.

```shell
export LS_IMAGE_TAG=5.3.10-220419-apache
docker compose -f docker-compose.yml -f docker-compose.test.yml up -d
```

## Integration tests

```shell
export LIMESURVEY_URL="http://localhost:8001/index.php/admin/remotecontrol"
export DB_URI="postgresql://limesurvey:secret@localhost:5432/limesurvey"

nox -rs tests --python "3.10" -- -m "integration_test"
```

### Run integraton tests on a specific Limesurvey version

```shell
export LIMESURVEY_URL="http://localhost:8001/index.php/admin/remotecontrol"
export DB_URI="postgresql://limesurvey:secret@localhost:5432/limesurvey"
export LS_IMAGE_TAG=5.3.10-220419-apache

docker-compose \
    -f docker-compose.yml \
    -f docker-compose.test.yml up \
    -d

nox -rs tests --python "3.10" -- -m "integration_test"
```

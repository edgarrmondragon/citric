# Common development tasks

Step-by-step recipes for tasks that come up often. For one-time setup, see [environment](/contributing/environment), and for test options, see [testing](/contributing/testing).

## Run checks

| Task | Command |
| :-------------------------------- | :------------------------------------ |
| List all Nox sessions | `./noxfile.py -l` |
| Unit tests (all Python versions) | `./noxfile.py -s test` |
| Unit tests on a single version | `./noxfile.py -s test-3.14` |
| Integration tests | `./noxfile.py -s integration` |
| Doctests | `./noxfile.py -s xdoctest` |
| Type checks (mypy, ty, pyright, pyrefly) | `./noxfile.py -s typing` |
| Dependency checks | `./noxfile.py -s deps` |
| Style checks | `prek run --all-files` |
| Build the docs | `./noxfile.py -s docs-build` |

Nox sessions marked as parallel run in parallel by default. The `integration` session is not parallel because it shares Docker ports.

## Run a subset of the integration tests

Integration tests start a LimeSurvey stack with Docker Compose (see [testing](/contributing/testing.md#integration-tests)), so the Docker daemon must be running.

```shell
./noxfile.py -s integration -- -k test_survey          # select tests by name
./noxfile.py -s integration -- -k test_survey --pdb    # drop into the debugger on failure
```

Everything after `--` is passed to pytest.

### Run alongside a manual stack

`tests/compose.yaml` publishes fixed host ports (`8001`, `5433`, `1025` and `8025`) for manual use:

```shell
docker compose -f tests/compose.yaml -f tests/compose.git-ref.yaml up
```

The integration tests set `LS_HTTP_PUBLISH`, `LS_DB_PUBLISH`, `LS_SMTP_PUBLISH` and `LS_MAILPIT_PUBLISH` to empty strings, so Docker picks free host ports and a manual stack doesn't interfere.

### Leftover containers

If a test run is killed, its containers (named `pytest<pid>-*`) can stay up. Make sure no pytest process is still running (and possibly paused in `--pdb`), then remove the stack:

```shell
docker compose -p pytest<pid> down -v
```

## Fix or add fields in a typed dictionary

The TypedDicts in `src/citric/types.py` describe what LimeSurvey returns. The integration tests validate real responses against them with {py:func}`typeguard.check_type`, for example:

```python
survey_props = check_type(client.get_survey_properties(survey_id), SurveyProperties)
```

To make a type pass without over-loosening it:

1. Run the integration test that exercises it and read the typeguard error. It names the offending key and the value the server returned.
1. Look up the field in the LimeSurvey source. The model's docblock (`@property`) lists the declared type, and its `rules()` method lists the allowed values (`'in', 'range' => [...]`). Prefer these over guessing from a single response:
   - Models live in [`application/models`](https://github.com/LimeSurvey/LimeSurvey/tree/develop-minor/application/models), for instance `Survey.php` and `SurveyLanguageSetting.php`.
   - RPC behavior is in `application/helpers/remotecontrol/`.
1. Use the narrowest type that matches the source: a `Literal[...]` for a validated set of codes, `int` or `str` for free values, and `| None` only for nullable columns.
1. Widen a type only when a real response fails the check. Add a docstring after each field that describes it, and link the LimeSurvey source when the value isn't obvious.
1. Mark fields that only exist in newer versions with `NotRequired[...]` and the directives described in [new LimeSurvey features](/contributing/new-limesurvey-features).
1. Re-run the integration test, and `./noxfile.py -s typing` for the static checkers.

To test against a different LimeSurvey version, see the `LS_IMAGE_TAG` and `LS_REF` settings in [testing](/contributing/testing.md#integration-tests).

## Add a changelog entry

Changelog entries use [Changie](https://changie.dev/). The `Issue` value is a GitHub issue or PR number:

```shell
changie new
```

This writes a YAML file to `.changes/unreleased/`. Kinds are configured in `.changie.yaml`.

## Release

See [release](/contributing/release).

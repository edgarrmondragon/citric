# AGENTS.md

Citric is a Python client for the LimeSurvey RemoteControl 2 (JSON-RPC) and REST APIs. Contributor documentation lives in [docs/contributing/](docs/contributing/index.md). Read the relevant page before starting a task.

| To do this... | Read |
| :--------------------------------------------------- | :--------------------------------------------------------------------- |
| Set up the environment, branch, commit, open a PR | [environment.md](docs/contributing/environment.md) |
| Run tests, integration tests, or choose a LimeSurvey version | [testing.md](docs/contributing/testing.md) |
| Run a single test, debug a failure, clear stuck Docker ports, fix a TypedDict against LimeSurvey's source, add a changelog entry | [dev-tasks.md](docs/contributing/dev-tasks.md) |
| Document a feature that needs a minimum LimeSurvey version | [new-limesurvey-features.md](docs/contributing/new-limesurvey-features.md) |
| Check LimeSurvey's source for RPC or REST API changes to keep Citric in sync | [limesurvey-sync skill](.claude/skills/limesurvey-sync/SKILL.md) |
| Build or serve the docs | [docs.md](docs/contributing/docs.md) |
| Update dependencies | [update-dependencies.md](docs/contributing/update-dependencies.md) |
| Cut a release | [release.md](docs/contributing/release.md) |

## Essentials

- Tooling is [uv](https://docs.astral.sh/uv/), [Nox](https://nox.thea.codes/) (`./noxfile.py -l` lists sessions) and [prek](https://github.com/j178/prek) for style checks (`prek run --all-files`).
- Unit tests: `./noxfile.py -s test`. Integration tests need Docker: `./noxfile.py -s integration -- -k <name>`.
- Type checks run four checkers: `./noxfile.py -s typing`.
- Types in `src/citric/types.py` are validated against real server responses with typeguard in the integration tests. Keep them as narrow as the LimeSurvey source allows.
- Add a changelog entry with `changie new` for user-facing changes.
- Don't commit, push, or remove Docker containers you didn't start without asking.

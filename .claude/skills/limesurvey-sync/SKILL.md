---
name: limesurvey-sync
description: Check LimeSurvey's source for RemoteControl 2 (RPC) and REST API changes that Citric doesn't cover yet. Use when asked to sync with a new LimeSurvey release, find missing or outdated API methods, routes or TypedDict fields, or audit API drift.
---

# Sync Citric with LimeSurvey's API

Report-only. Don't edit code, commit or push unless the user asks afterwards.

## 1. Get the upstream diff

```shell
./scripts/limesurvey_api_diff.py [--base <version>] [--target <version|branch>]
```

- `--base` defaults to the newest version pinned in `.github/tags.json`; `--target` defaults to the newest upstream release. Versions are bare (`7.5.1`) because Docker image dates don't match upstream tag dates. Use `--target master` to look ahead.
- Set `GITHUB_TOKEN` if you hit GitHub's anonymous rate limit.
- The script lists added, removed and re-signed RPC methods, added, removed and re-routed REST routes, and the changed files under the API paths. It doesn't read response fields. You do that in step 3.

## 2. Compare with Citric

| LimeSurvey | Citric |
| :-- | :-- |
| RPC method `snake_case_name` in `remotecontrol_handle.php` | Method of the same name on `citric.Client` in `src/citric/client.py` |
| REST route `VERB /rest/v1/...` | Method on the REST client in `src/citric/rest.py` |
| Response fields | TypedDicts in `src/citric/types.py` |

Search for each added, removed or re-signed item with Grep. For every one, classify it as:

- **Missing**: new upstream, not in Citric.
- **Stale**: removed or renamed upstream, still in Citric. Check `git grep` for the `minlimesurvey` directives to see which versions Citric claims to support before calling something removable.
- **Signature drift**: new, removed or renamed parameters. A new parameter with a default is usually additive.
- **Covered**: already handled.

## 3. Check response types

For each changed file under `Transformer/Output/` or `SchemaFactory/`, read the diff upstream, for example:

```shell
gh api "repos/LimeSurvey/LimeSurvey/compare/<base-tag>...<target-tag>" \
  --jq '.files[] | select(.filename | test("<name>")) | .patch'
```

Compare it with the matching TypedDict in `src/citric/types.py`. Follow [dev-tasks.md](../../../docs/contributing/dev-tasks.md#fix-or-add-fields-in-a-typed-dictionary) for how narrow to make types, and `NotRequired` for fields that only exist in newer versions. Refactors that don't change the output shape aren't drift.

## 4. Separate upstream bugs

If a diff looks like a regression in LimeSurvey rather than an API change, for example an endpoint that now returns a 500, report it separately. It needs an `xfail` in the integration tests, not a Citric change.

## 5. Report

Group findings as Missing, Stale, Signature drift, Type changes and Upstream bugs. For each, give the upstream file and what changed, the Citric file to touch, and the minimum LimeSurvey version for the `minlimesurvey` directive from [new-limesurvey-features.md](../../../docs/contributing/new-limesurvey-features.md). Skip empty groups.

Finish by offering to implement the changes, add tests, and run `changie new`.

```{eval-rst}
.. meta::
    :description:
        A Python client for the LimeSurvey Remote Control API 2.
```

# Citric

*A client to the [LimeSurvey Remote Control API 2](https://manual.limesurvey.org/RemoteControl_2_API), written in modern
Python.*

Release **v{sub-ref}`version`**. ([What's new?](./changelog.md))

```{include} ../README.md
:start-after: <!-- begin-short -->
:end-before: <!-- end-short -->
```

## Prerequisites

- Python 3.11+
- A LimeSurvey server with JSON RPC enabled (typically can be done at `/admin/globalsettings#interfaces`)
- A LimeSurvey username and password

## Supported versions

Integration tests are run against a LimeSurvey instance, and both PostgreSQL and MySQL backends, using Docker Compose. The following versions of LimeSurvey were tested for this release:

```{include} _partial/tags.md
```

But also the latest 6.x and 7.x are tested continuously and are expected to work.

## How-to guides

- [Automatically close the session with a context manager](guide/cookbook.md#automatically-close-the-session-with-a-context-manager)
- [Get surveys and questions](guide/cookbook.md#get-surveys-and-questions)
- [Export responses to a `pandas` dataframe](guide/cookbook.md#export-responses-to-a-pandas-dataframe)
- [Export responses to a DuckDB database and analyze with SQL](guide/cookbook.md#export-responses-to-a-duckdb-database-and-analyze-with-sql)
- [Change the default HTTP transport attributes](guide/cookbook.md#change-the-default-http-transport-attributes)
- [Use a different HTTP transport](guide/cookbook.md#use-a-different-http-transport)
- [Use a different authentication plugin](guide/cookbook.md#use-a-different-authentication-plugin)
- [Get files uploaded to a survey and move them to S3](guide/cookbook.md#get-files-uploaded-to-a-survey-and-move-them-to-s3)
- [Use the raw `Client.session` for low-level interaction](guide/cookbook.md#use-the-session-attribute-for-low-level-interaction)
- [Use with _R_ via `reticulate`](guide/cookbook.md#use-with-r-via-reticulate)
- [Notebook samples](guide/cookbook.md#notebook-samples)

```{toctree}
:maxdepth: 2
:hidden:
:caption: How-to guides

guide/cookbook
guide/transports
```

```{toctree}
:maxdepth: 2
:hidden:
:caption: Changelog

./changelog.md
```

```{toctree}
:maxdepth: 4
:hidden:
:caption: Reference

Python API reference <_api/index>
```

```{toctree}
:hidden:
:caption: API coverage

RPC method coverage <rpc_coverage>
REST endpoints coverage <rest_coverage>
```

```{toctree}
:maxdepth: 1
:hidden:
:caption: License

license
```

```{toctree}
:maxdepth: 1
:hidden:
:caption: Contributing

./contributing/index.md
```

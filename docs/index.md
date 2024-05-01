```{eval-rst}
.. meta::
    :description lang=en:
        A Python client for the LimeSurvey Remote Control API 2.
    :description lang=es:
        Un cliente de Python para la API de control remoto de LimeSurvey.
```

# Citric

*A client to the [LimeSurvey Remote Control API 2](https://manual.limesurvey.org/RemoteControl_2_API), written in modern
Python.*

Release **v{sub-ref}`version`**. ([What's new?](./changelog.md))

```{include} ../README.md
:start-after: <!-- begin-short -->
:end-before: <!-- end-short -->
```

### Integration tests

Integration tests are run against a LimeSurvey instance, and both PostgreSQL and MySQL backends, using Docker Compose. The following versions of LimeSurvey were tested for this release:

- {ls_tag}`6.5.3+240415`
- {ls_tag}`6.5.1+240320`
- {ls_tag}`6.5.0+240319`
- {ls_tag}`5.6.59+240416`
- {ls_tag}`5.6.57+240312`
- {ls_tag}`5.6.56+240227`

But also, the latest 5.x and 6.x are tested continuously and are expected to work.

## How-to guides

- [Automatically close the session with a context manager](how-to.md#automatically-close-the-session-with-a-context-manager)
- [Get surveys and questions](how-to.md#get-surveys-and-questions)
- [Export responses to a `pandas` dataframe](how-to.md#export-responses-to-a-pandas-dataframe)
- [Export responses to a DuckDB database and analyze with SQL](how-to.md#export-responses-to-a-duckdb-database-and-analyze-with-sql)
- [Change the default HTTP session attributes](how-to.md#change-the-default-http-session-attributes)
- [Use a custom `requests` session](how-to.md#use-a-custom-requests-session)
- [Use a different authentication plugin](how-to.md#use-a-different-authentication-plugin)
- [Get files uploaded to a survey and move them to S3](how-to.md#get-files-uploaded-to-a-survey-and-move-them-to-s3)
- [Use the raw `Client.session` for low-level interaction](how-to.md#use-the-session-attribute-for-low-level-interaction)
- [Notebook samples](how-to.md#notebook-samples)

```{toctree}
:maxdepth: 2
:hidden:

how-to
```

```{toctree}
:maxdepth: 2
:hidden:

./changelog.md
```

```{toctree}
:hidden:

RPC method coverage <rpc_coverage>
REST endpoints coverage <rest_coverage>
```

```{toctree}
:maxdepth: 4
:hidden:

Python API reference <_api/index>
```

```{toctree}
:maxdepth: 1
:hidden:

license
```

```{toctree}
:caption: Contributing
:hidden:

contributing/code-of-conduct
contributing/getting-started
contributing/environment
contributing/testing
contributing/docs
contributing/docker
contributing/release
contributing/unreleased-features
```

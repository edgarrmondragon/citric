```{eval-rst}
.. meta::
    :description:
        How-to guides for the Citric LimeSurvey client.
```

# Cookbook

For the full JSON-RPC reference, see the [RemoteControl 2 API docs][rc2api].

## Automatically close the session with a context manager

```{literalinclude} ../snippets/code_samples/context_manager.py
:start-after: start example
:end-before: end example
```

Otherwise, you can manually close the session with {meth}`client.close() <citric.Client.close>`.

## Get surveys and questions

```{literalinclude} ../snippets/code_samples/get_surveys.py
:start-after: start example
:end-before: end example
```

## Run requests concurrently with `asyncio`

Citric doesn't have an async API (yet), but its blocking client can be used from
`asyncio` code with {func}`asyncio.to_thread`. Each call runs in a worker thread, so
independent calls, like fetching the properties of many surveys, overlap instead of
running one after the other. Authentication is thread-safe, so concurrent calls on a
new client share a single session key.

Worker threads share the client's HTTP transport. Both
{class}`~citric.transport.urllib3.Urllib3Transport` and
{class}`~citric.transport.httpx2.Httpx2Transport` are considered safe for
concurrent use.

:::{caution}
If you pass a {py:class}`requests.Session` instance as the transport, note that it isn't 100% guaranteed to be thread-safe.
:::

The samples use {func}`asyncio.gather` with `return_exceptions=True` so that every worker
thread has finished before the client is closed. Cancelling an `asyncio` task doesn't stop
its thread, so if the surrounding coroutine itself is cancelled, calls already running
may still be in flight when the client closes.

```{literalinclude} ../snippets/code_samples/asyncio_to_thread.py
:start-after: start example
:end-before: end example
```

To limit the load on the server, bound the concurrency with a semaphore and size the
connection pool accordingly. With {class}`~citric.transport.urllib3.Urllib3Transport`
that's `maxsize`; with {class}`~citric.transport.httpx2.Httpx2Transport`, it's
`max_connections` and `max_keepalive_connections`; with {py:class}`requests.Session`,
mount an {py:class}`~requests.adapters.HTTPAdapter` with `pool_maxsize`:

```{literalinclude} ../snippets/code_samples/asyncio_to_thread_bounded.py
:start-after: start example
:end-before: end example
```

## Create and import questions using Python objects

Use {class}`citric.objects.Question` to compose questions programmatically and
import them with {meth}`client.import_question() <citric.Client.import_question>`.

```{literalinclude} ../snippets/code_samples/import_question.py
:start-after: start example
:end-before: end example
```

## Update question answers using the REST API

```{literalinclude} ../snippets/code_samples/update_question_answer_rest.py
:start-after: start example
:end-before: end example
```

## Export responses to a `pandas` dataframe

```{literalinclude} ../snippets/code_samples/pandas_df.py
:start-after: start example
:end-before: end example
```

## Export responses to a [DuckDB](https://duckdb.org/) database and analyze with SQL

```{literalinclude} ../snippets/code_samples/duckdb_sql.py
:start-after: start example
:end-before: end example
```

## Use a different HTTP transport

You can read more about the subject in the d[edicated guide](./transports.md).

```{literalinclude} ../snippets/code_samples/custom_transport.py
:start-after: start example
:end-before: end example
```

## Use a different authentication plugin

By default, this client uses the internal database for authentication but
{ls_manual}`different plugins <Authentication_plugins>` are supported using the
`auth_plugin` argument.

```{literalinclude} ../snippets/code_samples/auth_plugin.py
:start-after: start example
:end-before: end example
```

Common plugins are `Authdb` (default), `AuthLDAP` and `Authwebserver`.

## Upload files and use them to update a response

```{literalinclude} ../snippets/code_samples/uploaded_to_response.py
:start-after: start example
:end-before: end example
```

## Get files uploaded to a survey and move them to S3

```{literalinclude} ../snippets/code_samples/upload_s3.py
:start-after: start example
:end-before: end example
```

## Use the session attribute for low-level interaction

This library doesn't implement all RPC methods, so if you're in dire need of using a method not currently supported, you can use the `session` attribute to invoke the underlying RPC interface without having to pass a session key explicitly:

```{literalinclude} ../snippets/code_samples/session_attr.py
:start-after: start example
:end-before: end example
```

## Use with _R_ via [reticulate]

If you prefer using _R_ instead of _Python_, you can use the `reticulate` package to get survey data downloaded with `citric`.

Write a Python script to get the survey data, making sure to assign a dataframe to a variable (e.g., `survey_data`):

```{literalinclude} ../snippets/code_samples/reticulate.py
:start-after: start example
:end-before: end example
```

Then, in _R_, use the `reticulate` package to call the Python script and use the `df` variable:

```{literalinclude} ../snippets/code_samples/citric.R
:start-after: start example
:end-before: end example
```

## Notebook samples

- [Import a survey file from S3](https://github.com/edgarrmondragon/citric/blob/main/docs/notebooks/import_s3.ipynb)
- [Download responses and analyze them with DuckDB](https://github.com/edgarrmondragon/citric/blob/main/docs/notebooks/duckdb.ipynb)
- [Download responses and save them to a SQLite database](https://github.com/edgarrmondragon/citric/blob/main/docs/notebooks/pandas_sqlite.ipynb)

[rc2api]: https://api.limesurvey.org/classes/remotecontrol_handle.html
[reticulate]: https://rstudio.github.io/reticulate/

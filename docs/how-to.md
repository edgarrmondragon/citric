# How-to Guide

For the full JSON-RPC reference, see the [RemoteControl 2 API docs][rc2api].

## Automatically close the session with a context manager

```{literalinclude} ../code_samples/context_manager.py
:start-after: start example
:end-before: end example
```

Otherwise, you can manually close the session with {meth}`client.close() <citric.client.Client.close>`.

## Get surveys and questions

```{literalinclude} ../code_samples/get_surveys.py
:start-after: start example
:end-before: end example
```

## Export responses to a `pandas` dataframe

```{literalinclude} ../code_samples/pandas_df.py
:start-after: start example
:end-before: end example
```

## Export responses to a [DuckDB](https://duckdb.org/) database and analyze with SQL

```{literalinclude} ../code_samples/duckdb_sql.py
:start-after: start example
:end-before: end example
```

## Change the default HTTP session attributes

```{literalinclude} ../code_samples/requests_session_attributes.py
:start-after: start example
:end-before: end example
```

## Use a custom `requests` session

It's possible to use a custom session object to make requests. For example, to cache the requests
and reduce the load on your server in read-intensive applications, you can use
[`requests-cache`](inv:requests-cache:std#general):

```{literalinclude} ../code_samples/custom_requests_session.py
:start-after: start example
:end-before: end example
```

## Use a different authentication plugin

By default, this client uses the internal database for authentication but
{ls_manual}`different plugins <Authentication_plugins>` are supported using the
`auth_plugin` argument.

```{literalinclude} ../code_samples/auth_plugin.py
:start-after: start example
:end-before: end example
```

Common plugins are `Authdb` (default), `AuthLDAP` and `Authwebserver`.

## Get files uploaded to a survey and move them to S3

```{literalinclude} ../code_samples/upload_s3.py
:start-after: start example
:end-before: end example
```

## Use the session attribute for low-level interaction

This library doesn't implement all RPC methods, so if you're in dire need of using a method not currently supported, you can use the `session` attribute to invoke the underlying RPC interface without having to pass a session key explicitly:

```{literalinclude} ../code_samples/session_attr.py
:start-after: start example
:end-before: end example
```

## Notebook samples

- [Import a survey file from S3](https://github.com/edgarrmondragon/citric/blob/main/docs/notebooks/import_s3.ipynb)
- [Download responses and analyze them with DuckDB](https://github.com/edgarrmondragon/citric/blob/main/docs/notebooks/duckdb.ipynb)
- [Download responses and save them to a SQLite database](https://github.com/edgarrmondragon/citric/blob/main/docs/notebooks/pandas_sqlite.ipynb)

[rc2api]: https://api.limesurvey.org/classes/remotecontrol_handle.html

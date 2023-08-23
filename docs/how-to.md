# How-to Guide

For the full JSON-RPC reference, see the [RemoteControl 2 API docs][rc2api].

## Automatically close the session with a context manager

```python
from citric import Client

LS_URL = "http://localhost:8001/index.php/admin/remotecontrol"

with Client(LS_URL, "iamadmin", "secret") as client:
    # Do stuff with the client
    ...
```

Otherwise, you can manually close the session with {meth}`client.close() <citric.client.Client.close>`.

## Get surveys and questions

```python
from citric import Client

LS_URL = "http://localhost:8001/index.php/admin/remotecontrol"

client = Client(LS_URL, "iamadmin", "secret")

# Get all surveys from user "iamadmin"
surveys = client.list_surveys("iamadmin")

for s in surveys:
    print(s["surveyls_title"])

    # Get all questions, regardless of group
    questions = client.list_questions(s["sid"])
    for q in questions:
        print(q["title"], q["question"])
```

## Export responses to a `pandas` dataframe

```python
import io
import pandas as pd
from citric import Client

survey_id = 123456

client = citric.Client(...)

# Export responses to CSV and read into a Pandas DataFrame
df = pd.read_csv(
    io.BytesIO(client.export_responses(survey_id, file_format="csv")),
    delimiter=";",
    parse_dates=["datestamp", "startdate", "submitdate"],
    index_col="id",
)
```

## Export responses to a [DuckDB](https://duckdb.org/) database and analyze with SQL

```python
import citric
import duckdb

client = citric.Client(...)

with open("responses.csv", "wb") as file:
    file.write(client.export_responses(<your survey ID>, file_format="csv"))

duckdb.execute("CREATE TABLE responses AS SELECT * FROM 'responses.csv'")
duckdb.sql("""
    SELECT
        token,
        submitdate - startdate AS duration
    FROM responses
    ORDER BY 2 DESC
    LIMIT 10
""").show()
```

## Use custom `requests` session

It's possible to use a custom session object to make requests. For example, to cache the requests
and reduce the load on your server in read-intensive applications, you can use
[`requests-cache`](inv:requests-cache:std#general):

```python
import requests_cache

cached_session = requests_cache.CachedSession(
    expire_after=60,
    allowable_methods=["POST"],
)

client = Client(
    LS_URL,
    "iamadmin",
    "secret",
    requests_session=cached_session,
)

# Get all surveys from user "iamadmin".
# All responses will be cached for 1 minute.
surveys = client.list_surveys("iamadmin")
```

## Use a different authentication plugin

By default, this client uses the internal database for authentication but
{ls_manual}`arbitrary plugins <Authentication_plugins>` are supported by the
`auth_plugin` argument.

```python
client = Client(
    LS_URL,
    "iamadmin",
    "secret",
    auth_plugin="AuthLDAP",
)
```

Common plugins are `Authdb` (default), `AuthLDAP` and `Authwebserver`.

## Get files uploaded to a survey and move them to S3

```python
import boto3
from citric import Client

s3 = boto3.client("s3")

client = Client(
    "https://mylimeserver.com/index.php/admin/remotecontrol",
    "iamadmin",
    "secret",
)

survey_id = 12345

# Get all uploaded files and upload them to S3
for file in client.get_uploaded_file_objects(survey_id):
    s3.upload_fileobj(
        file.content,
        "my-s3-bucket",
        f"uploads/sid={survey_id}/qid={file.meta.question.qid}/{file.meta.filename}",
    )
```

## Use the raw `Client.session` for low-level interaction

This library doesn't (yet) implement all RPC methods, so if you're in dire need of using a method not currently supported, you can use the `session` attribute to invoke the underlying RPC interface without having to pass a session key explicitly:

```python
client = Client(LS_URL, "iamadmin", "secret")

# Call the copy_survey method, not available in Client
new_survey_id = client.session.copy_survey(35239, "copied_survey")
```

## Notebook samples

- [Import a survey file from S3](https://github.com/edgarrmondragon/citric/blob/main/docs/notebooks/import_s3.ipynb)
- [Download responses and analyze them with DuckDB](https://github.com/edgarrmondragon/citric/blob/main/docs/notebooks/duckdb.ipynb)
- [Download responses and save them to a SQLite database](https://github.com/edgarrmondragon/citric/blob/main/docs/notebooks/pandas_sqlite.ipynb)

[rc2api]: https://api.limesurvey.org/classes/remotecontrol_handle.html

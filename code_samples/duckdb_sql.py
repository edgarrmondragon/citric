"""Export survey responses to a DuckDB database."""

from __future__ import annotations

# ruff: noqa: I001, PTH123, FURB103

# start example
from pathlib import Path

import citric
import duckdb

client = citric.Client(
    "https://mylimeserver.com/index.php/admin/remotecontrol",
    "iamadmin",
    "secret",
)

Path("responses.csv").write_bytes(client.export_responses(12345, file_format="csv"))

duckdb.execute("CREATE TABLE responses AS SELECT * FROM 'responses.csv'")
duckdb.sql("""
    SELECT
        token,
        submitdate - startdate AS duration
    FROM responses
    ORDER BY 2 DESC
    LIMIT 10
""").show()
# end example

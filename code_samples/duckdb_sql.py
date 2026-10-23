# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Export survey responses to a DuckDB database."""

# ruff: file-ignore[print]

from __future__ import annotations

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
top_10 = duckdb.execute("""
    SELECT
        token,
        submitdate - startdate AS duration
    FROM responses
    ORDER BY 2 DESC
    LIMIT 10
""").fetchall()

for token, duration in top_10:
    print(f"Respondent {token} took {round(duration.total_seconds() / 60, 1)} minutes")
# end example

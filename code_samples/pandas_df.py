"""Export survey responses to a Pandas DataFrame."""

from __future__ import annotations

# ruff: noqa: PD901, S106
# start example
import io

import pandas as pd
from citric import Client

survey_id = 123456

client = Client(
    "https://mylimeserver.com/index.php/admin/remotecontrol",
    "iamadmin",
    "secret",
)

# Export responses to CSV and read into a Pandas DataFrame
df = pd.read_csv(
    io.BytesIO(client.export_responses(survey_id, file_format="csv")),
    delimiter=";",
    parse_dates=["datestamp", "startdate", "submitdate"],
    index_col="id",
)
# end example

"""Use reticulate to export LimeSurvey data to R."""

# ruff: noqa: T201

from __future__ import annotations

# start example
# export_ls_responses.py
import io

import citric
import pandas as pd

client = citric.Client(
    "http://localhost:8001/index.php/admin/remotecontrol",
    "iamadmin",
    "secret",
)
data = client.export_responses(123456, file_format="csv")
survey_data = pd.read_csv(
    io.BytesIO(data),
    delimiter=";",
    parse_dates=["datestamp", "startdate", "submitdate"],
    index_col="id",
)
# end example

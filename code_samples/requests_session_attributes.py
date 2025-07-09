"""Modify attributes of the `requests` session used by the client."""

from __future__ import annotations

# start example
import requests
from citric import Client

session = requests.Session()

# Set custom headers to be sent on each request
# https://requests.readthedocs.io/en/latest/api/#requests.Session.headers
session.headers["My-Custom-Header"] = "My-Custom-Value"

client = Client(
    "https://mylimeserver.com/index.php/admin/remotecontrol",
    "iamadmin",
    "secret",
    requests_session=session,
)
# end example

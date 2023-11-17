"""Modify attributes of the `requests` session used by the client."""

from __future__ import annotations

# start example
import requests
from citric import Client

session = requests.Session()

# Set to False to accept any TLS certificate presented by the server
# https://requests.readthedocs.io/en/latest/api/#requests.Session.verify
session.verify = False

client = Client(
    "https://mylimeserver.com/index.php/admin/remotecontrol",
    "iamadmin",
    "secret",
    requests_session=session,
)
# end example

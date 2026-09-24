# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Example of using a non-`requests` HTTP transport with the client."""

from __future__ import annotations

# start example
from citric import Client
from citric.transport.httpx2 import Httpx2Transport

client = Client(
    "https://example.com/index.php/admin/remotecontrol",
    "iamadmin",
    "secret",
    requests_session=Httpx2Transport(),
)

surveys = client.list_surveys("iamadmin")
# end example

# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Example of deferring authentication."""

from __future__ import annotations

# start example
from citric import Client

# No request is made yet
client = Client(
    "https://example.com/index.php/admin/remotecontrol",
    "iamadmin",
    "secret",
    connect=False,
)

# The session key is retrieved on the first call that needs it
surveys = client.list_surveys()
# end example

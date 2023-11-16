"""Example of using the context manager to automatically clean up the session key."""

from __future__ import annotations

# start example
from citric import Client

LS_URL = "http://localhost:8001/index.php/admin/remotecontrol"

with Client(LS_URL, "iamadmin", "secret") as client:
    # Do stuff with the client
    ...
# end example

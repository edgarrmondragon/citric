"""Example of using an auth plugin."""

from __future__ import annotations

# start example
from citric import Client

client = Client(
    "https://example.com/index.php/admin/remotecontrol",
    "iamadmin",
    "secret",
    auth_plugin="AuthLDAP",
)
# end example

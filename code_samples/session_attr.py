"""Example of using the Client.session attribute to call RPC methods directly."""

from __future__ import annotations

from citric import Client

# start example
client = Client(
    "https://mylimeserver.com/index.php/admin/remotecontrol",
    "iamadmin",
    "secret",
)

# Get the raw response from mail_registered_participants
result = client.session.call("mail_registered_participants", 35239)

# Get the raw response from remind_participants
result = client.session.call("remind_participants", 35239)
# end example

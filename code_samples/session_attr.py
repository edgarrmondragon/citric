"""Example of using the RPC.session attribute to call RPC methods directly."""

from __future__ import annotations

from citric import RPC

# start example
client = RPC(
    "https://mylimeserver.com/index.php/admin/remotecontrol",
    "iamadmin",
    "secret",
)

# Get the raw response from mail_registered_participants
result = client.session.call("mail_registered_participants", 35239)

# Get the raw response from remind_participants
result = client.session.call("remind_participants", 35239)
# end example

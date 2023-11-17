"""Example of using the Client.session attribute to call RPC methods directly."""

from __future__ import annotations

from citric import Client

# start example
client = Client(
    "https://mylimeserver.com/index.php/admin/remotecontrol",
    "iamadmin",
    "secret",
)

# Call the not_available_in_client method, not available in the Client
new_survey_id = client.session.not_available_in_client(35239, "copied_survey")
# end example

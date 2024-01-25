"""Example of using the RPC.session attribute to call RPC methods directly."""

from __future__ import annotations

from citric import RPC

# start example
client = RPC(
    "https://mylimeserver.com/index.php/admin/remotecontrol",
    "iamadmin",
    "secret",
)

# Call the not_available_in_client method, not available in the RPC class
new_survey_id = client.session.not_available_in_client(35239, "copied_survey")
# end example

"""Example of using the Client.session attribute to call RPC methods directly."""

from __future__ import annotations

from citric import Client

# start example
client = Client(..., "iamadmin", "secret")

# Call the copy_survey method, not available in Client
new_survey_id = client.session.copy_survey(35239, "copied_survey")
# end example

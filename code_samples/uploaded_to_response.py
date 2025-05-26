"""Upload files to a LimeSurvey question and add them to a response."""

# ruff : noqa: PTH123, S105

from __future__ import annotations

# start example
import json

from citric import Client

PARTICIPANT_TOKEN = "T00000"

survey_id = 12
group_id = 34
question_id = 56

# You can also find the field name by using client.get_fieldmap(survey_id)
field_name = f"{survey_id}X{group_id}X{question_id}"

with Client(
    "http://localhost:8001/index.php/admin/remotecontrol",
    "iamadmin",
    "secret",
) as client:
    # Upload files to the question using the field name
    with open("image_1.png", "rb") as file:
        content1 = file.read()
        result1 = client.upload_file_object(survey_id, field_name, "image_1.png", file)

    with open("image_2.png", "rb") as file:
        content2 = file.read()
        result2 = client.upload_file_object(survey_id, field_name, "image_2.png", file)

    # Add a response
    response_files = [result1, result2]
    responses = [
        {
            "token": PARTICIPANT_TOKEN,
            field_name: json.dumps(response_files),
            f"{field_name}_filecount": len(response_files),
        },
    ]

    # Download files
    paths = client.download_files("./downloads", survey_id, PARTICIPANT_TOKEN)
# end example

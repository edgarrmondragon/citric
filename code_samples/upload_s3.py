"""Upload survey files to S3."""

from __future__ import annotations

# start example
import json

import boto3
from citric import Client

s3 = boto3.client("s3")

client = Client(
    "https://mylimeserver.com/index.php/admin/remotecontrol",
    "iamadmin",
    "secret",
)

survey_id = 12345
exported = json.loads(client.export_responses(survey_id, file_format="json"))

# Get all uploaded files for all responses and upload them to S3
for response in exported["responses"]:
    for file in client.get_uploaded_file_objects(survey_id, response_id=response["id"]):
        filename = (
            f"uploads/sid={survey_id}/qid={file['meta']['question']['qid']}"
            f"/{response['id']}/{file['meta']['filename']}"
        )
        s3.upload_fileobj(file["content"], "my-s3-bucket", filename)
# end example

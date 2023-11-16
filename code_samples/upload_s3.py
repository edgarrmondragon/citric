"""Upload survey files to S3."""

from __future__ import annotations

# start example
import boto3
from citric import Client

s3 = boto3.client("s3")

client = Client(
    "https://mylimeserver.com/index.php/admin/remotecontrol",
    "iamadmin",
    "secret",
)

survey_id = 12345

# Get all uploaded files and upload them to S3
for file in client.get_uploaded_file_objects(survey_id):
    s3.upload_fileobj(
        file.content,
        "my-s3-bucket",
        f"uploads/sid={survey_id}/qid={file.meta.question.qid}/{file.meta.filename}",
    )
# end example

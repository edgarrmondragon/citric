"""Get all surveys and questions from user "iamadmin"."""

# ruff: noqa: T201

from __future__ import annotations

# start example
from citric import Client

LS_URL = "http://localhost:8001/index.php/admin/remotecontrol"

client = Client(LS_URL, "iamadmin", "secret")

# Get all surveys from user "iamadmin"
surveys = client.list_surveys("iamadmin")

for s in surveys:
    print(s["surveyls_title"])

    # Get all questions, regardless of group
    questions = client.list_questions(s["sid"])
    for q in questions:
        print(q["title"], q["question"])
# end example

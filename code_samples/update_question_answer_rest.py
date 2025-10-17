"""Example: Update question answer properties using the REST API."""

# ruff: noqa: T201

from __future__ import annotations

# start example
from citric._rest import RESTClient  # noqa: PLC2701

# Create REST client
client = RESTClient(
    "https://example.com/rest/v1",
    "your_username",
    "your_password",
)

survey_id = 142423

# Get survey details
survey = client.get_survey(survey_id)
print(survey)

# Inspect question 247 to find answer IDs
for question in survey["questionGroups"][0]["questions"]:
    if answers := question.get("answers"):
        print("Answers for question", question["qid"])
        for answer in answers:
            print(f"  Answer ID: {answer['aid']}, Code: {answer['code']}")

# Define patch operations
operations = [
    {
        "entity": "answer",
        "op": "update",
        # Question ID
        "id": 247,
        "props": [
            {
                # Answer ID
                "aid": 31,
                "code": "AO01",
                "sortOrder": 1,
                "assessmentValue": 0,
                "scaleId": 1,
                "l10ns": {
                    "de": {"answer": "ANTW1 scale 1", "language": "de"},
                    "en": {"answer": "ANS1 scale 1", "language": "en"},
                },
            },
            {
                # Answer ID
                "aid": 32,
                "code": "AO02",
                "sortOrder": 1,
                "assessmentValue": 0,
                "scaleId": 1,
                "l10ns": {
                    "de": {"answer": "ANTW2 scale 1", "language": "de"},
                    "en": {"answer": "ANS2 scale 1", "language": "en"},
                },
            },
            {
                # Answer ID
                "aid": 33,
                "code": "AO03",
                "sortOrder": 1,
                "assessmentValue": 0,
                "scaleId": 1,
                "l10ns": {
                    "de": {"answer": "ANTW3 scale 1", "language": "de"},
                    "en": {"answer": "ANS3 scale 1", "language": "en"},
                },
            },
        ],
    }
]


result = client.patch_survey(survey_id, operations)
print(f"Operations applied: {result['operationsApplied']}")
# end example

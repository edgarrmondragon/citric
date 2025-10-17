# REST endpoints coverage

| Name | Implemented |
| :----------------------------------------- | :-------------------------------------------------- |
| `POST /rest/v1/session` | [Yes](citric.RESTClient.authenticate) |
| `DELETE /rest/v1/session` | [Yes](citric.RESTClient.close) |
| `GET /rest/v1/survey` | [Yes](citric.RESTClient.get_surveys) |
| `GET /rest/v1/survey-detail/{survey_id}` | [Yes](citric.RESTClient.get_survey_details) |
| `PATCH /rest/v1/survey-detail/{survey_id}` | [Yes](citric.RESTClient.patch_survey) |

# REST endpoints coverage

| Name | Implemented |
| :----------------------------------------- | :-------------------------------------------------- |
| `POST /rest/v1/session` | [Yes](citric.RESTClient.authenticate) |
| `DELETE /rest/v1/session` | [Yes](citric.RESTClient.close) |
| `GET /rest/v1/survey` | [Yes](citric.RESTClient.get_surveys) |
| `GET /rest/v1/survey-detail/{survey_id}` | [Yes](citric.RESTClient.get_survey_details) |
| `PATCH /rest/v1/survey-detail/{survey_id}` | [Yes](citric.RESTClient.patch_survey) |
| `POST /rest/v1/survey-import` | [Yes](citric.RESTClient.import_survey) |
| `POST /rest/v1/survey-responses/{survey_id}` | [Yes](citric.RESTClient.get_survey_responses) |
| `POST /rest/v1/survey-responses-export/{survey_id}` | [Yes](citric.RESTClient.export_survey_responses) |
| `GET /rest/v1/statistics-overview/{survey_id}` | [Yes](citric.RESTClient.get_statistics_overview) |
| `GET /rest/v1/statistics-glance/{survey_id}` | [Yes](citric.RESTClient.get_statistics_glance) |
| `GET /rest/v1/statistics/{survey_id}` | [Yes](citric.RESTClient.get_statistics) |
| `GET /rest/v1/version-info` | [Yes](citric.RESTClient.get_version_info) |
| `GET /rest/v1/survey-groups` | [Yes](citric.RESTClient.get_survey_groups) |
| `GET /rest/v1/survey-group-list` | [Yes](citric.RESTClient.get_survey_groups) |

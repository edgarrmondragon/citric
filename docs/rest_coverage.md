# REST endpoints coverage

| Name                                       | Implemented                                         |
| :----------------------------------------- | :-------------------------------------------------- |
| `POST /rest/v1/session`                    | [Yes](citric._rest.RESTClient.authenticate)          |
| `DELETE /rest/v1/session`                  | [Yes](citric._rest.RESTClient.close)                 |
| `GET /rest/v1/survey`                      | [Yes](citric._rest.RESTClient.get_surveys)           |
| `GET /rest/v1/survey-detail/{survey_id}`   | [Yes](citric._rest.RESTClient.get_survey_details)    |
| `PATCH /rest/v1/survey-detail/{survey_id}` | [Yes](citric._rest.RESTClient.update_survey_details) |

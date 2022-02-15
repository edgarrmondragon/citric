# API coverage

|              Name              | Implemented |                                    Description                                    |
|:-------------------------------|:-----------:|:----------------------------------------------------------------------------------|
| `activate_survey`              | Yes         | Activate survey (RPC function)                                                    |
| `activate_tokens`              | Yes         | Activate survey participants (RPC function)                                       |
| `add_group`                    | Yes         | Add empty group with minimum details (RPC function)                               |
| `add_language`                 | Yes         | Add a survey language (RPC function)                                              |
| `add_participants`             | Yes         | Add participants to the survey.                                                   |
| `add_response`                 | Yes         | Add a response to the survey responses collection.                                |
| `add_survey`                   | Yes         | Add an empty survey with minimum details                                          |
| `copy_survey`                  | Yes         | Copy survey (RPC function)                                                        |
| `cpd_importParticipants`       | No          | Import a participant into the LimeSurvey CPDB                                     |
| `delete_group`                 | Yes         | Delete a group from a chosen survey (RPC function)                                |
| `delete_language`              | No          | Delete a language from a survey (RPC function)                                    |
| `delete_participants`          | Yes         | Delete multiple participants from the survey participants table (RPC function)    |
| `delete_question`              | No          | Delete question from a survey (RPC function)                                      |
| `delete_response`              | Yes         | Delete a response in a given survey using its Id                                  |
| `delete_survey`                | Yes         | Delete a survey.                                                                  |
| `export_responses`             | Yes         | Export responses in base64 encoded string                                         |
| `export_responses_by_token`    | Yes         | Export token response in a survey.                                                |
| `export_statistics`            | No          | Export survey statistics (RPC function)                                           |
| `export_timeline`              | No          | Export submission timeline (RPC function)                                         |
| `get_group_properties`         | Yes         | Get the properties of a group of a survey .                                       |
| `get_language_properties`      | Yes         | Get survey language properties (RPC function)                                     |
| `get_participant_properties`   | Yes         | Get settings of a survey participant (RPC function)                               |
| `get_question_properties`      | Yes         | Get properties of a question in a survey.                                         |
| `get_response_ids`             | Yes         | Find response IDs given a survey ID and a token (RPC function)                    |
| `get_session_key`              | Yes         | Create and return a session key.                                                  |
| `get_site_settings`            | Yes         | Get a global setting                                                              |
| `get_summary`                  | No          | Get survey summary, regarding token usage and survey participation (RPC function) |
| `get_survey_properties`        | Yes         | Get survey properties (RPC function)                                              |
| `get_uploaded_files`           | Yes         | Obtain all uploaded files for all responses                                       |
| `import_group`                 | Yes         | Import a group and add to a survey (RPC function)                                 |
| `import_question`              | Yes         | Import question (RPC function)                                                    |
| `import_survey`                | Yes         | Import survey in a known format (RPC function)                                    |
| `invite_participants`          | No          | Invite participants in a survey (RPC function)                                    |
| `list_groups`                  | Yes         | Get survey groups (RPC function)                                                  |
| `list_participants`            | Yes         | Return the IDs and properties of survey participants (RPC function)               |
| `list_questions`               | Yes         | Return the ids and info of (sub-)questions of a survey/group (RPC function)       |
| `list_survey_groups`           | Yes         | List the survey groups belonging to a user                                        |
| `list_surveys`                 | Yes         | List the survey belonging to a user (RPC function)                                |
| `list_users`                   | Yes         | Get list the ids and info of administration user(s) (RPC function)                |
| `mail_registered_participants` | No          | Send e-mails to registered participants in a survey (RPC function)                |
| `release_session_key`          | Yes         | Close the RPC session                                                             |
| `remind_participants`          | No          | Send a reminder to participants in a survey (RPC function)                        |
| `set_group_properties`         | No          | Set group properties (RPC function)                                               |
| `set_language_properties`      | No          | Set survey language properties (RPC function)                                     |
| `set_participant_properties`   | No          | Set properties of a survey participant (RPC function)                             |
| `set_question_properties`      | No          | Set question properties.                                                          |
| `set_quota_properties`         | No          | Set quota attributes (RPC function)                                               |
| `set_survey_properties`        | No          | Set survey properties (RPC function)                                              |
| `update_response`              | No          | Update a response in a given survey.                                              |
| `upload_file`                  | No          | Uploads one file to be used later.                                                |

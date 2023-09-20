# RPC method coverage

Full list of methods is available at [the Remote Control documentation](https://api.limesurvey.org/classes/remotecontrol_handle.html).

| Name                           | Implemented                                   | Description                                                                       |
| :----------------------------- | :-------------------------------------------- | :-------------------------------------------------------------------------------- |
| `activate_survey`              | [Yes](citric.RPC.activate_survey)             | Activate survey (RPC function)                                                    |
| `activate_tokens`              | [Yes](citric.RPC.activate_tokens)             | Activate survey participants (RPC function)                                       |
| `add_group`                    | [Yes](citric.RPC.add_group)                   | Add empty group with minimum details (RPC function)                               |
| `add_language`                 | [Yes](citric.RPC.add_language)                | Add a survey language (RPC function)                                              |
| `add_participants`             | [Yes](citric.RPC.add_participants)            | Add participants to the survey.                                                   |
| `add_quota`                    | [Yes](citric.RPC.add_quota)                   | Add a new quota with minimum details                                              |
| `add_response`                 | [Yes](citric.RPC.add_response)                | Add a response to the survey responses collection.                                |
| `add_survey`                   | [Yes](citric.RPC.add_survey)                  | Add an empty survey with minimum details                                          |
| `copy_survey`                  | [Yes](citric.RPC.copy_survey)                 | Copy survey (RPC function)                                                        |
| `cpd_importParticipants`       | [Yes](citric.RPC.import_cpdb_participants)    | Import a participant into the LimeSurvey CPDB                                     |
| `delete_group`                 | [Yes](citric.RPC.delete_group)                | Delete a group from a chosen survey (RPC function)                                |
| `delete_language`              | [Yes](citric.RPC.delete_language)             | Delete a language from a survey (RPC function)                                    |
| `delete_participants`          | [Yes](citric.RPC.delete_participants)         | Delete multiple participants from the survey participants table (RPC function)    |
| `delete_question`              | [Yes](citric.RPC.delete_question)             | Delete question from a survey (RPC function)                                      |
| `delete_quota`                 | [Yes](citric.RPC.delete_quota)                | Delete a quota                                                                    |
| `delete_response`              | [Yes](citric.RPC.delete_response)             | Delete a response in a given survey using its Id                                  |
| `delete_survey`                | [Yes](citric.RPC.delete_survey)               | Delete a survey.                                                                  |
| `export_responses`             | [Yes](citric.RPC.export_responses)            | Export responses in base64 encoded string                                         |
| `export_responses_by_token`    | [Yes](citric.RPC.export_responses)            | Export token response in a survey.                                                |
| `export_statistics`            | [Yes](citric.RPC.export_statistics)           | Export survey statistics (RPC function)                                           |
| `export_timeline`              | [Yes](citric.RPC.export_timeline)             | Export submission timeline (RPC function)                                         |
| `get_available_site_settings`  | [Yes](citric.RPC.get_available_site_settings) | Get the available site settings                                                   |
| `get_fieldmap`                 | [Yes](citric.RPC.get_fieldmap)                | Returns the requested survey's fieldmap in an array                               |
| `get_group_properties`         | [Yes](citric.RPC.get_group_properties)        | Get the properties of a group of a survey .                                       |
| `get_language_properties`      | [Yes](citric.RPC.get_language_properties)     | Get survey language properties (RPC function)                                     |
| `get_participant_properties`   | [Yes](citric.RPC.get_participant_properties)  | Get settings of a survey participant (RPC function)                               |
| `get_question_properties`      | [Yes](citric.RPC.get_question_properties)     | Get properties of a question in a survey.                                         |
| `get_quota_properties`         | [Yes](citric.RPC.get_quota_properties)        | Get quota attributes (RPC function)                                               |
| `get_response_ids`             | [Yes](citric.RPC.get_response_ids)            | Find response IDs given a survey ID and a token (RPC function)                    |
| `get_session_key`              | [Yes](Session)                                | Create and return a session key.                                                  |
| `get_site_settings`            | [Yes](citric.RPC.get_default_theme)           | Get a global setting                                                              |
| `get_summary`                  | [Yes](citric.RPC.get_summary)                 | Get survey summary, regarding token usage and survey participation (RPC function) |
| `get_survey_properties`        | [Yes](citric.RPC.get_survey_properties)       | Get survey properties (RPC function)                                              |
| `get_uploaded_files`           | [Yes](citric.RPC.get_uploaded_files)          | Obtain all uploaded files for all responses                                       |
| `import_group`                 | [Yes](citric.RPC.import_group)                | Import a group and add to a survey (RPC function)                                 |
| `import_question`              | [Yes](citric.RPC.import_question)             | Import question (RPC function)                                                    |
| `import_survey`                | [Yes](citric.RPC.import_survey)               | Import survey in a known format (RPC function)                                    |
| `invite_participants`          | [Yes](citric.RPC.invite_participants)         | Invite participants in a survey (RPC function)                                    |
| `list_groups`                  | [Yes](citric.RPC.list_groups)                 | Get survey groups (RPC function)                                                  |
| `list_participants`            | [Yes](citric.RPC.list_participants)           | Return the IDs and properties of survey participants (RPC function)               |
| `list_questions`               | [Yes](citric.RPC.list_questions)              | Return the ids and info of (sub-)questions of a survey/group (RPC function)       |
| `list_quotas`                  | [Yes](citric.RPC.list_quotas)                 | List the quotas in a survey                                                       |
| `list_survey_groups`           | [Yes](citric.RPC.list_survey_groups)          | List the survey groups belonging to a user                                        |
| `list_surveys`                 | [Yes](citric.RPC.list_surveys)                | List the survey belonging to a user (RPC function)                                |
| `list_users`                   | [Yes](citric.RPC.list_users)                  | Get list the ids and info of administration user(s) (RPC function)                |
| `mail_registered_participants` | No                                            | Send e-mails to registered participants in a survey (RPC function)                |
| `release_session_key`          | [Yes](Session.close)                          | Close the RPC session                                                             |
| `remind_participants`          | No                                            | Send a reminder to participants in a survey (RPC function)                        |
| `set_group_properties`         | [Yes](citric.RPC.set_group_properties)        | Set group properties (RPC function)                                               |
| `set_language_properties`      | [Yes](citric.RPC.set_language_properties)     | Set survey language properties (RPC function)                                     |
| `set_participant_properties`   | [Yes](citric.RPC.set_participant_properties)  | Set properties of a survey participant (RPC function)                             |
| `set_question_properties`      | [Yes](citric.RPC.set_question_properties)     | Set question properties.                                                          |
| `set_quota_properties`         | [Yes](citric.RPC.set_quota_properties)        | Set quota attributes (RPC function)                                               |
| `set_survey_properties`        | [Yes](citric.RPC.set_survey_properties)       | Set survey properties (RPC function)                                              |
| `update_response`              | [Yes](citric.RPC.update_response)             | Update a response in a given survey.                                              |
| `upload_file`                  | [Yes](citric.RPC.upload_file)                 | Uploads one file to be used later.                                                |

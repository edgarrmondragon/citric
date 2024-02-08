# RPC method coverage

Full list of methods is available at [the Remote Control documentation](https://api.limesurvey.org/classes/remotecontrol_handle.html).

| Name                           | Implemented                                                         | Description                                                                       |
| :----------------------------- | :------------------------------------------------------------------ | :-------------------------------------------------------------------------------- |
| `activate_survey`              | [Yes](citric.Client.activate_survey)                                | Activate survey (RPC function)                                                    |
| `activate_tokens`              | [Yes](citric.Client.activate_tokens)                                | Activate survey participants (RPC function)                                       |
| `add_group`                    | [Yes](citric.Client.add_group)                                      | Add empty group with minimum details (RPC function)                               |
| `add_language`                 | [Yes](citric.Client.add_language)                                   | Add a survey language (RPC function)                                              |
| `add_participants`             | [Yes](citric.Client.add_participants)                               | Add participants to the survey.                                                   |
| `add_quota`                    | [Yes](citric.Client.add_quota)                                      | Add a new quota with minimum details                                              |
| `add_response`                 | [Yes](citric.Client.add_response)                                   | Add a response to the survey responses collection.                                |
| `add_survey`                   | [Yes](citric.Client.add_survey)                                     | Add an empty survey with minimum details                                          |
| `copy_survey`                  | [Yes](citric.Client.copy_survey)                                    | Copy survey (RPC function)                                                        |
| `cpd_importParticipants`       | [Yes](citric.Client.import_cpdb_participants)                       | Import a participant into the LimeSurvey CPDB                                     |
| `delete_group`                 | [Yes](citric.Client.delete_group)                                   | Delete a group from a chosen survey (RPC function)                                |
| `delete_language`              | [Yes](citric.Client.delete_language)                                | Delete a language from a survey (RPC function)                                    |
| `delete_participants`          | [Yes](citric.Client.delete_participants)                            | Delete multiple participants from the survey participants table (RPC function)    |
| `delete_question`              | [Yes](citric.Client.delete_question)                                | Delete question from a survey (RPC function)                                      |
| `delete_quota`                 | [Yes](citric.Client.delete_quota)                                   | Delete a quota                                                                    |
| `delete_response`              | [Yes](citric.Client.delete_response)                                | Delete a response in a given survey using its Id                                  |
| `delete_survey`                | [Yes](citric.Client.delete_survey)                                  | Delete a survey.                                                                  |
| `export_responses`             | [Yes](citric.Client.export_responses)                               | Export responses in base64 encoded string                                         |
| `export_responses_by_token`    | [Yes](citric.Client.export_responses)                               | Export token response in a survey.                                                |
| `export_statistics`            | [Yes](citric.Client.export_statistics)                              | Export survey statistics (RPC function)                                           |
| `export_timeline`              | [Yes](citric.Client.export_timeline)                                | Export submission timeline (RPC function)                                         |
| `get_available_site_settings`  | [Yes](citric.Client.get_available_site_settings)                    | Get the available site settings                                                   |
| `get_fieldmap`                 | [Yes](citric.Client.get_fieldmap)                                   | Returns the requested survey's fieldmap in an array                               |
| `get_group_properties`         | [Yes](citric.Client.get_group_properties)                           | Get the properties of a group of a survey .                                       |
| `get_language_properties`      | [Yes](citric.Client.get_language_properties)                        | Get survey language properties (RPC function)                                     |
| `get_participant_properties`   | [Yes](citric.Client.get_participant_properties)                     | Get settings of a survey participant (RPC function)                               |
| `get_question_properties`      | [Yes](citric.Client.get_question_properties)                        | Get properties of a question in a survey.                                         |
| `get_quota_properties`         | [Yes](citric.Client.get_quota_properties)                           | Get quota attributes (RPC function)                                               |
| `get_response_ids`             | [Yes](citric.Client.get_response_ids)                               | Find response IDs given a survey ID and a token (RPC function)                    |
| `get_session_key`              | [Yes](Session)                                                      | Create and return a session key.                                                  |
| `get_site_settings`            | [Yes](citric.Client.get_default_theme)                              | Get a global setting                                                              |
| `get_summary`                  | [Yes](citric.Client.get_summary)                                    | Get survey summary, regarding token usage and survey participation (RPC function) |
| `get_survey_properties`        | [Yes](citric.Client.get_survey_properties)                          | Get survey properties (RPC function)                                              |
| `get_uploaded_files`           | [Yes](citric.Client.get_uploaded_files)                             | Obtain all uploaded files for all responses                                       |
| `import_group`                 | [Yes](citric.Client.import_group)                                   | Import a group and add to a survey (RPC function)                                 |
| `import_question`              | [Yes](citric.Client.import_question)                                | Import question (RPC function)                                                    |
| `import_survey`                | [Yes](citric.Client.import_survey)                                  | Import survey in a known format (RPC function)                                    |
| `invite_participants`          | [Yes](citric.Client.invite_participants)                            | Invite participants in a survey (RPC function)                                    |
| `list_groups`                  | [Yes](citric.Client.list_groups)                                    | Get survey groups (RPC function)                                                  |
| `list_participants`            | [Yes](citric.Client.list_participants)                              | Return the IDs and properties of survey participants (RPC function)               |
| `list_questions`               | [Yes](citric.Client.list_questions)                                 | Return the ids and info of (sub-)questions of a survey/group (RPC function)       |
| `list_quotas`                  | [Yes](citric.Client.list_quotas)                                    | List the quotas in a survey                                                       |
| `list_survey_groups`           | [Yes](citric.Client.list_survey_groups)                             | List the survey groups belonging to a user                                        |
| `list_surveys`                 | [Yes](citric.Client.list_surveys)                                   | List the survey belonging to a user (RPC function)                                |
| `list_users`                   | [Yes](citric.Client.list_users)                                     | Get list the ids and info of administration user(s) (RPC function)                |
| `mail_registered_participants` | [No](how-to.md#use-the-session-attribute-for-low-level-interaction) | Send e-mails to registered participants in a survey (RPC function)                |
| `release_session_key`          | [Yes](Session.close)                                                | Close the RPC session                                                             |
| `remind_participants`          | [No](how-to.md#use-the-session-attribute-for-low-level-interaction) | Send a reminder to participants in a survey (RPC function)                        |
| `set_group_properties`         | [Yes](citric.Client.set_group_properties)                           | Set group properties (RPC function)                                               |
| `set_language_properties`      | [Yes](citric.Client.set_language_properties)                        | Set survey language properties (RPC function)                                     |
| `set_participant_properties`   | [Yes](citric.Client.set_participant_properties)                     | Set properties of a survey participant (RPC function)                             |
| `set_question_properties`      | [Yes](citric.Client.set_question_properties)                        | Set question properties.                                                          |
| `set_quota_properties`         | [Yes](citric.Client.set_quota_properties)                           | Set quota attributes (RPC function)                                               |
| `set_survey_properties`        | [Yes](citric.Client.set_survey_properties)                          | Set survey properties (RPC function)                                              |
| `update_response`              | [Yes](citric.Client.update_response)                                | Update a response in a given survey.                                              |
| `upload_file`                  | [Yes](citric.Client.upload_file)                                    | Uploads one file to be used later.                                                |

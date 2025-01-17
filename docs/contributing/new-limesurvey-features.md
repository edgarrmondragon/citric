# New LimeSurvey Features

If a feature is added to Citric that is only available starting from a specific version of LimeSurvey, one of the following Sphinx directives should be added to the docstring of the new feature:

- The `.. minlimesurvey` directive will add a note to the documentation that the feature is only available starting from a specific version of LimeSurvey.
- The `.. minlimesurveyparam` directive will add a note to the documentation that the method parameter is only available starting from a specific version of LimeSurvey.
- The `.. minlimesurveyattribute` directive will add a warning to the documentation that the attribute is only available starting from a specific version of LimeSurvey.

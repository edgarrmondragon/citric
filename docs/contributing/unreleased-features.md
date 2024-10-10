# Unreleased Features

Citric supports LimeSurvey features that are not yet released and are sitting in the [`master`](https://github.com/LimeSurvey/LimeSurvey/tree/master) or [`develop`](https://github.com/LimeSurvey/LimeSurvey/tree/develop) branches of the LimeSurvey repository. These features must be decorated with {func}`@future <citric._compat.future>` or {func}`@future_parameter <citric._compat.future_parameter>` in order to be warn users that they are using a feature that is not yet released.

There are also Sphinx directives that can be used to document these features:

- The `.. future` directive will add a warning to the documentation that the method is not yet supported in any released version of LimeSurvey.
- The `.. futureparam` directive will add a warning to the documentation that the parameter is not yet supported in any released version of LimeSurvey.

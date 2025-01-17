"""A Sphinx extension to add a directive for next LimeSurvey version."""

from __future__ import annotations

import typing as t

from docutils import nodes
from docutils.parsers.rst import Directive

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx

__all__ = [
    "Attribute",
    "Feature",
    "Parameter",
    "setup",
]


class Feature(Directive):
    """A directive for LimeSurvey features added in a certain version.

    Adds a note to features only available after some release of LimeSurvey.
    """

    required_arguments = 1
    feature_type = "method"
    admonition_type = nodes.note

    def run(self) -> list[nodes.Node]:
        limesurvey_version = self.arguments[0]
        text = nodes.paragraph(
            "",
            "",
            nodes.Text(
                f"This {self.feature_type} is only supported in LimeSurvey "
                f"{limesurvey_version} and above."
            ),
        )
        return [self.admonition_type("", text)]


class Parameter(Directive):
    """A directive for released parameters.

    Adds a note to method parameters that are only available after some release of
    LimeSurvey.
    """

    required_arguments = 2
    admonition_type = nodes.note

    def run(self) -> list[nodes.Node]:
        limesurvey_version, parameter = self.arguments[:2]
        text = nodes.paragraph(
            "",
            "",
            nodes.Text("The parameter "),
            nodes.literal("", parameter),
            nodes.Text(
                f" is only supported in LimeSurvey {limesurvey_version} and above."
            ),
        )
        return [self.admonition_type("", text)]


class Attribute(Feature):
    """A directive for released attributes.

    Adds a note to class attributes that are only available after some release of
    LimeSurvey.
    """

    feature_type = "attribute"
    admonition_type = nodes.warning


def setup(app: Sphinx) -> dict[str, t.Any]:
    app.add_directive("minlimesurvey", Feature)
    app.add_directive("minlimesurveyparam", Parameter)
    app.add_directive("minlimesurveyattribute", Attribute)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

"""A Sphinx extension to add a directive for next LimeSurvey version."""

from __future__ import annotations

import typing as t

from docutils import nodes
from docutils.parsers.rst import Directive

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx

__all__ = ["ReleasedFeature", "UnreleasedFeature", "setup"]


class UnreleasedFeature(Directive):
    """A directive for development-only features.

    Adds a warning to features only available until the next minor release of
    LimeSurvey.
    """

    required_arguments = 1
    message = "This method is only supported in LimeSurvey >= {next_version}."
    admonition_type = nodes.warning

    def run(self) -> list[nodes.Node]:
        next_version = self.arguments[0]
        text = self.message.format(next_version=next_version)
        return [self.admonition_type("", nodes.paragraph(text=text))]


class UnreleasedParameter(Directive):
    """A directive for development-only parameters.

    Adds a warning to method parameters that are only available in the next minor
    release of LimeSurvey.
    """

    required_arguments = 2
    message = (
        "The parameter {parameter} is only supported in LimeSurvey >= {next_version}."
    )
    admonition_type = nodes.warning

    def run(self) -> list[nodes.Node]:
        next_version, parameter = self.arguments[:2]
        text = self.message.format(next_version=next_version, parameter=parameter)
        return [self.admonition_type("", nodes.paragraph(text=text))]


class ReleasedFeature(UnreleasedFeature):
    """A directive for released features.

    Adds a note to features only available after some release of LimeSurvey.
    """

    message = "This method is only supported in LimeSurvey >= {next_version}."
    admonition_type = nodes.note


class ReleasedParameter(UnreleasedParameter):
    """A directive for released parameters.

    Adds a note to method parameters that are only available after some release of
    LimeSurvey.
    """

    message = (
        "The parameter {parameter} is only supported in LimeSurvey >= {next_version}."
    )
    admonition_type = nodes.note


def setup(app: Sphinx) -> dict[str, t.Any]:
    app.add_directive("future", UnreleasedFeature)
    app.add_directive("futureparam", UnreleasedParameter)
    app.add_directive("minlimesurvey", ReleasedFeature)
    app.add_directive("minlimesurveyparam", ReleasedParameter)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

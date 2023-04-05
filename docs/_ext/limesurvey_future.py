"""A Sphinx extension to add a directive for next LimeSurvey version."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from docutils import nodes
from docutils.parsers.rst import Directive

if TYPE_CHECKING:
    from sphinx.application import Sphinx

__all__ = ["ReleasedFeature", "UnreleasedFeature", "setup"]


class UnreleasedFeature(Directive):
    """A directive for development-only features.

    Adds a warning to features only available until the next minor release of
    LimeSurvey.
    """

    required_arguments = 1
    message = (
        "This method is only supported in LimeSurvey >= {next_version} "
        "(currently in development)."
    )
    admonition_type = nodes.warning

    def run(self) -> list[nodes.Node]:
        next_version = self.arguments[0]
        text = self.message.format(next_version=next_version)
        return [self.admonition_type("", nodes.paragraph(text=text))]


class ReleasedFeature(UnreleasedFeature):
    """A directive for released features.

    Adds a note to features only available after some release of LimeSurvey.
    """

    message = "This method is only supported in LimeSurvey >= {next_version}."
    admonition_type = nodes.note


def setup(app: Sphinx) -> dict[str, Any]:
    app.add_directive("future", UnreleasedFeature)
    app.add_directive("minlimesurvey", ReleasedFeature)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

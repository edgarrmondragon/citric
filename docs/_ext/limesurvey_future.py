"""A Sphinx extension to add a directive for next LimeSurvey version."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from docutils import nodes
from docutils.parsers.rst import Directive

if TYPE_CHECKING:
    from sphinx.application import Sphinx


class UnreleasedFeature(Directive):
    """A directive for development-only features.

    Adds a warning to features only available until the next minor release of
    LimeSurvey.
    """

    required_arguments = 1

    def run(self) -> list[nodes.Node]:
        next_version = self.arguments[0]
        admonition_node = nodes.warning(
            "",
            nodes.paragraph(
                text=(
                    f"This method is only available in LimeSurvey >= {next_version} "
                    "(currently in development)."
                ),
            ),
        )
        return [admonition_node]


def setup(app: Sphinx) -> dict[str, Any]:
    app.add_directive("future", UnreleasedFeature)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

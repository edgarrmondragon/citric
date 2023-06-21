"""Sphinx configuration."""

from __future__ import annotations

import sys
import typing as t
from pathlib import Path

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx

sys.path.append(str(Path("./_ext").resolve()))

project = "citric"
author = "Edgar Ramírez Mondragón"
project_copyright = f"2020, {author}"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.linkcode",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "autoapi.extension",
    "myst_parser",
    "sphinx_copybutton",
    "limesurvey_future",
]

autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"

autoapi_type = "python"
autoapi_root = "_api"
autoapi_dirs = [
    Path("../src").resolve(),
]
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
    "special-members",
    "imported-members",
    "private-members",
]

html_extra_path = [
    "googled10b55fb460af091.html",
    "code.png",
]
html_theme = "furo"
html_theme_options = {
    "navigation_with_keys": True,
}
html_title = "Citric, a Python client for LimeSurvey"

extlinks = {
    "rpc_method": (
        "https://api.limesurvey.org/classes/remotecontrol_handle.html#method_%s",
        "RPC method %s",
    ),
    "ls_manual": (
        "https://manual.limesurvey.org/%s",
        "%s",
    ),
}

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

napoleon_custom_sections = [
    ("Keys", "params_style"),
]


def linkcode_resolve(domain: str, info: dict) -> str | None:
    """Get URL to source code.

    Args:
        domain: Language domain the object is in.
        info: A dictionary with domain-specific keys.

    Returns:
        A URL.
    """
    if domain != "py":
        return None
    if not info["module"]:
        return None
    filename = info["module"].replace(".", "/")
    return f"https://github.com/edgarrmondragon/citric/tree/main/src/{filename}.py"


def skip_member_filter(
    app: Sphinx,  # noqa: ARG001
    what: str,  # noqa: ARG001
    name: str,
    obj: t.Any,  # noqa: ARG001, ANN401
    skip: bool,  # noqa: FBT001
    options: t.Any,  # noqa: ARG001, ANN401
) -> bool | None:
    """Filter autoapi members.

    Args:
        app: Sphinx application object.
        what: The type of the object which the docstring belongs to.
        name: The fully qualified name of the object.
        obj: The object itself.
        skip: Whether AutoAPI will skip this member if the handler does not override
            the decision.
        options: The options given to the directive.

    Returns:
        Whether to skip the member.
    """
    if name == "citric.client.Client":
        skip = True
    return skip


def setup(sphinx: Sphinx) -> None:
    """Setup function.

    Args:
        sphinx: Sphinx application object.
    """
    sphinx.connect("autoapi-skip-member", skip_member_filter)

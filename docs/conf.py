"""Sphinx configuration."""

from __future__ import annotations

import sys
import typing as t
from pathlib import Path

import citric

sys.path.append(str(Path("./_ext").resolve()))

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx

# -- Project information ---------------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "citric"

author = "Edgar Ramírez Mondragón"
project_copyright = f"2020, {author}"
version = citric.__version__
release = citric.__version__

# -- General configuration -------------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.linkcode",
    "sphinx.ext.napoleon",
    "autoapi.extension",
    "myst_parser",
    "sphinx_copybutton",
    "limesurvey_future",
    "hoverxref.extension",
    "notfound.extension",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

nitpicky = True
nitpick_ignore = {
    ("py:class", "citric.types.Result"),
    ("py:class", "Result"),
    ("py:class", "YesNo"),
    ("py:class", "T"),
    ("py:obj", "T"),
}

# -- Options for internationalization --------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-internationalization

# -- Options for Math ------------------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-math

# -- Options for HTML output -----------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_theme_options = {
    "navigation_with_keys": True,
    "source_repository": "https://github.com/edgarrmondragon/citric/",
    "source_branch": "main",
    "source_directory": "docs/",
}
html_title = "Citric, a Python client for LimeSurvey"
html_extra_path = [
    "googled10b55fb460af091.html",
    "code.png",
]

# -- Options for Autodoc ---------------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#configuration

autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"

# -- Options for extlinks --------------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/extlinks.html

extlinks = {
    "rpc_method": (
        "https://api.limesurvey.org/classes/remotecontrol-handle.html#method_%s",
        "RPC method %s",
    ),
    "ls_manual": (
        "https://manual.limesurvey.org/%s",
        "%s",
    ),
    "ls_tag": (
        "https://github.com/LimeSurvey/LimeSurvey/releases/tag/%s",
        "%s",
    ),
}

# -- Options for intersphinx -----------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#configuration

intersphinx_mapping = {
    "requests": ("https://requests.readthedocs.io/en/latest/", None),
    "requests-cache": ("https://requests-cache.readthedocs.io/en/stable/", None),
    "python": ("https://docs.python.org/3/", None),
}

# -- Options for linkcode --------------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/linkcode.html#configuration


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


# -- Options for Napoleon --------------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html#configuration

# -- Options for AutoAPI ---------------------------------------------------------------
# https://sphinx-autoapi.readthedocs.io/en/latest/reference/config.html

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
autoapi_root = "_api"

# -- Options for Myst ------------------------------------------------------------------
# https://myst-parser.readthedocs.io/en/latest/configuration.html

myst_heading_anchors = 2

# -- Options for hoverxref -------------------------------------------------------------
# https://sphinx-hoverxref.readthedocs.io/en/latest/configuration.html

hoverxref_role_types = {
    "hoverxref": "tooltip",
    "ref": "modal",
    "mod": "modal",
    "class": "tooltip",
}
hoverxref_default_type = "tooltip"
hoverxref_domains = [
    "py",
]
hoverxref_intersphinx = [
    "requests",
]


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
    if name == "citric.rest.client":
        skip = True
    return skip


def setup(sphinx: Sphinx) -> None:
    """Setup function.

    Args:
        sphinx: Sphinx application object.
    """
    sphinx.connect("autoapi-skip-member", skip_member_filter)

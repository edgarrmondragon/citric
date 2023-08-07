"""Sphinx configuration."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path("./_ext").resolve()))

project = "citric"
author = "Edgar Ramírez Mondragón"
project_copyright = f"2020, {author}"
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

hoverxref_default_type = "tooltip"

intersphinx_mapping = {
    "requests": ("https://requests.readthedocs.io/en/latest/", None),
    "requests-cache": ("https://requests-cache.readthedocs.io/en/stable/", None),
    "python": ("https://docs.python.org/3/", None),
}

hoverxref_intersphinx = [
    "requests",
    "python",
]

hoverxref_domains = [
    "py",
]

hoverxref_role_types = {
    "hoverxref": "tooltip",
    "ref": "modal",
    "mod": "modal",
    "class": "modal",
}

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

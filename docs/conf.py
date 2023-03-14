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
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "autoapi.extension",
    "myst_parser",
    "sphinx_copybutton",
    "sphinxext.opengraph",
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

ogp_site_name = "Citric"
ogp_image = "code.png"
ogp_image_alt = "Citric sample code"
ogp_enable_meta_description = True

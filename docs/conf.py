"""Sphinx configuration."""

from __future__ import annotations

import os

project = "citric"
author = "Edgar Ramírez Mondragón"
copyright = f"2020, {author}"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "autoapi.extension",
    "myst_parser",
    "nbsphinx",
]

autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"

autoapi_type = "python"
autoapi_root = "_api"
autoapi_dirs = [
    os.path.abspath("../src"),
]
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
    "special-members",
    "imported-members",
]

html_theme = "furo"
html_theme_options = {
    "navigation_with_keys": True,
}
html_title = "Citric"

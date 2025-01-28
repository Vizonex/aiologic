#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Ilya Egorov <0x42005e1f@gmail.com>
# SPDX-License-Identifier: CC0-1.0

from importlib.metadata import version as get_version

from packaging.version import parse as parse_version

project = "aiologic"
author = "Ilya Egorov"
copyright = "2025 Ilya Egorov"

v = parse_version(get_version("aiologic"))
version = v.base_version
release = v.public

extensions = [
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_inline_tabs",
    "sphinx_rtd_theme",
    "myst_parser",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

html_theme = "sphinx_rtd_theme"
html_theme_options = {}
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
html_context = {
    "display_github": True,
    "github_user": "x42005e1f",
    "github_repo": "aiologic",
    "github_version": "main",
    "conf_py_path": "/docs/",
}

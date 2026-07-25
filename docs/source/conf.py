# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

from sphinx.application import Sphinx

sys.path.insert(0, os.path.abspath("../.."))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Raito"
copyright = "2025, Aiden"
author = "Aiden"
release = "1.5.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions: list[str] = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
]

templates_path: list[str] = ["_templates"]
exclude_patterns: list[str] = []

autodoc_typehints = "description"
autodoc_member_order = "bysource"
autodoc_default_options = {
    "members": True,
    "show-inheritance": True,
    "ignore-module-all": True,
}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "aiogram": ("https://docs.aiogram.dev/en/latest", None),
}

language = os.environ.get("READTHEDOCS_LANGUAGE", "en")
locale_dirs = ["locale/"]
gettext_compact = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path: list[str] = ["_static"]
html_title = "Raito"


def run_apidoc(app: Sphinx) -> None:
    from sphinx.ext import apidoc

    here = os.path.dirname(__file__)
    apidoc.main(
        [
            "--force",
            "--separate",
            "--no-toc",
            "--implicit-namespaces",
            "--module-first",
            "--output-dir",
            os.path.join(here, "reference", "_apidoc"),
            os.path.join(here, "..", "..", "raito"),
        ]
    )


def setup(app: Sphinx) -> None:
    app.connect("builder-inited", run_apidoc)

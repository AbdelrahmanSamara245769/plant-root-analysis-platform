import os
import sys

sys.path.insert(0, os.path.abspath("../src"))

project = "CV4"
copyright = "2026, project team"
author = "Project team"
release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
]

html_theme = "sphinx_rtd_theme"

import os
import sys
from datetime import date

# Add src to path for sphinx-click or autodoc
sys.path.insert(0, os.path.abspath("../../src"))

project = "asv-spyglass"
copyright = f"{date.today().year}, Rohit Goswami"
author = "Rohit Goswami"

# The full version, including alpha/beta/rc tags
try:
    from asv_spyglass import __version__ as version
except ImportError:
    version = "0.1.0"
release = version

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_click",
]

templates_path = ["_templates"]
exclude_patterns = []

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]

myst_enable_extensions = [
    "colon_fence",
    "deflist",
]

html_theme_options = {
    "github_url": "https://github.com/airspeed-velocity/asv_spyglass",
    "use_edit_page_button": True,
}

html_context = {
    "github_user": "airspeed-velocity",
    "github_repo": "asv_spyglass",
    "github_version": "main",
    "doc_path": "docs/source",
}

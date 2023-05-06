# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

#########################################
# THIS IS IMPORTANT!
import os
import sys

sys.path.insert(0, os.path.abspath(".."))
#########################################

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "NeuroRuler"
copyright = '2023, Jesse Wei, Madison Lester, Peifeng "Hank" He, Eric Schneider'
author = 'Jesse Wei, Madison Lester, Peifeng "Hank" He, Eric Schneider'
release = ""

with open("../setup.py", "r") as f:
    for line in f:
        if line.strip().startswith("version"):
            release = line.split('"')[1]
            break

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx.ext.autodoc",
    "sphinx_rtd_theme",
    # For parsing Markdown
    "m2r2",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
source_suffix = [".rst", ".md", ".markdown"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# Good themes: python_docs_theme and sphinx_rtd_theme (looks amazing but has ads)
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# Source: https://stackoverflow.com/questions/59215996/how-to-add-a-logo-to-my-readthedocs-logo-rendering-at-0px-wide
html_static_path = ["_static"]
html_favicon = "nr_logo.ico"
html_logo = "_static/nr_logo.jpg"
html_theme_options = {
    "logo_only": True,
    "display_version": False,
}


# Prevents __init__ from being ignored
# Source: https://stackoverflow.com/questions/5599254/how-to-use-sphinxs-autodoc-to-document-a-classs-init-self-method
def skip(app, what, name, obj, would_skip, options):
    if name == "__init__":
        return False
    return would_skip


def setup(app):
    app.connect("autodoc-skip-member", skip)

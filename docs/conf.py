# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.extlinks",
    "sphinx.ext.ifconfig",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
]
source_suffix = ".rst"
master_doc = "index"
project = "humiolib"
year = "2020"
author = "Humio ApS"
copyright = "{0}, {1}".format(year, author)
version = "0.2.3"

pygments_style = "trac"
templates_path = ["."]
extlinks = {
    "issue": ("https://github.com/humio/python-humio/issues/%s", "#"),
    "pr": ("https://github.com/humio/python-humio/pulls/%s", "PR #"),
}


import sphinx_rtd_theme

extensions = [
    "sphinx_rtd_theme",
    "sphinx.ext.autodoc"
]

html_theme = "sphinx_rtd_theme"

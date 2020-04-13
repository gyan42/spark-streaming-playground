# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
from recommonmark.parser import CommonMarkParser
from unittest.mock import MagicMock
from recommonmark.transform import AutoStructify
sys.path.insert(0, os.path.abspath('../../src/'))


# TODO: https://github.com/rtfd/recommonmark/issues/93
# TODO https://github.com/rtfd/recommonmark/issues/120
# This patch helps in linking markdown files within mardown files
from recommonmark.states import DummyStateMachine
# Monkey patch to fix recommonmark 0.4 doc reference issues.
orig_run_role = DummyStateMachine.run_role
def run_role(self, name, options=None, content=None):
    if name == 'doc':
        name = 'any'
    return orig_run_role(self, name, options, content)
DummyStateMachine.run_role = run_role


# -- Project information -----------------------------------------------------

project = 'spark-streaming-playground'
copyright = '2020, Mageswaran Dhandapani'
author = 'Mageswaran Dhandapani'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['recommonmark',
              'sphinx.ext.autodoc',
              'sphinx.ext.autosummary',
              'sphinx.ext.doctest',
              'sphinx.ext.intersphinx',
              'sphinx.ext.todo',
              'sphinx.ext.coverage',
              'sphinx.ext.mathjax',
              'sphinx.ext.ifconfig',
              'sphinx.ext.viewcode',
              'sphinx_markdown_tables',
              # 'sphinxarg.ext',
              # 'm2r', # https://github.com/miyakogi/m2r/pull/55
              'sphinx.ext.githubpages']
              # 'sphinxcontrib.bibtex',
              # 'sphinx.ext.napoleon',
              # 'nbsphinx', #https://nbsphinx.readthedocs.io/en/0.6.0/
              # 'sphinx_issues', # https://github.com/sloria/sphinx-issues
              # 'sphinx_copybutton']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# www.sphinx-doc.org/en/stable/markdown.html
# https://github.com/sphinx-doc/sphinx/issues/7000
source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}
source_parsers = {
    '.md': CommonMarkParser,
}

# The short X.Y version.
version = '0.0.1'
# The full version, including alpha/beta/rc tags.
release = '0.0.1'


# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'


# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Output file base name for HTML help builder.
htmlhelp_basename = 'sspdoc'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_context = {
    'css_files': [
        'https://fonts.googleapis.com/css?family=Lato',
        '_static/css/custom_theme.css'
    ],
}



# At the bottom of conf.py
# https://recommonmark.readthedocs.io/en/latest/auto_structify.html
def setup(app):
    app.add_config_value('recommonmark_config', {
        'enable_auto_toc_tree' : True,
        'enable_math': True,
        'enable_inline_math': True,
    }, True)
    app.add_transform(AutoStructify)
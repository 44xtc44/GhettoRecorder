# Configuration file for the Sphinx documentation builder.
# https://shunsvineyard.info/2019/09/19/use-sphinx-for-python-documentation/
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

# -- Project information -----------------------------------------------------
# pip install -U sphinx
# !!! indentation of sphinx is mostly 3 leading spaces, code 4, block need one free line above and colon for head
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
# pip install -U sphinx
# pip install sphinx-rtd-theme
# pip install sphinxcontrib-napoleon
# Use sphinx-apidoc to build your API documentation:
# $ cd docs
# sphinx-apidoc -f -o source/ ../ghettorecorder/
# make html

project = 'GhettoRecorder'
copyright = 'MIT 2023, René Horn'
author = 'René Horn'
# release = '2.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Add napoleon to the extensions list
extensions = [
    'sphinx.ext.napoleon',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosectionlabel'
]


# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
pygments_style = 'sphinx'

html_static_path = ['_static']
html_logo = "./_static/ghetto_url.svg"
html_logo_only = True
html_display_version = False
html_css_files = [
    "css-style.css",
]

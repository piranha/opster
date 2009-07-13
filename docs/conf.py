# -*- coding: utf-8 -*-

import sys, os

sys.path.append('..')

# -- General configuration -----------------------------------------------------

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.doctest']
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = u'Finaloption'
copyright = u'2009, Alexander Solovyov'
version = '0.9'
release = '0.9'
exclude_trees = ['_build']
pygments_style = 'sphinx'


# -- Options for HTML output ---------------------------------------------------

html_theme = 'default'
# "<project> v<release> documentation".
#html_title = None
# A shorter title for the navigation bar.  Default is the same as html_title.
#html_short_title = None

#html_logo = None
#html_favicon = None
html_static_path = ['_static']
html_use_smartypants = True
htmlhelp_basename = 'Finaloptiondoc'


# -- Options for LaTeX output --------------------------------------------------

latex_documents = [
  ('index', 'Finaloption.tex', u'Finaloption Documentation',
   u'Alexander Solovyov', 'manual'),
]

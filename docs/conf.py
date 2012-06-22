# -*- coding: utf-8 -*-

import sys
from docutils.parsers import rst
sys.path.insert(0, '..')
import opster

# -- Add the hidden directive --------------------------------------------------

class HiddenDirective(rst.Directive):
    '''An rst directive that ignores all text in its block'''
    has_content = True
    def run(self):
        return []

rst.directives.register_directive('hidden', HiddenDirective)

# -- Doctest setup -------------------------------------------------------------

doctest_path = ['scripts']

# -- General configuration -----------------------------------------------------

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.doctest']
source_suffix = '.rst'
master_doc = 'index'
project = u'Opster'
copyright = u'2009-2011, Alexander Solovyov'
version = release = opster.__version__
exclude_trees = ['_build']

# -- Options for HTML output ---------------------------------------------------

# html_theme = 'cleanery'
# html_theme_path = ['.']
html_title = "%s v%s" % (project, version)

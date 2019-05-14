import os
import sys
sys.path.append(os.path.abspath('../..'))

import limis.core.utilities


project = 'limis'
copyright = '2019, Philip Streck'
author = 'Philip Streck'

version = limis.core.utilities.get_version()
release = limis.core.utilities.get_version()


extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.coverage',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
language = None
exclude_patterns = []
pygments_style = 'sphinx'

html_theme = 'basic'
html_theme_path = ['_themes']
html_static_path = ['_static']

htmlhelp_basename = 'limisdoc'

latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '10pt',
    'preamble': '',
    'figure_align': 'htbp',
}

latex_documents = [
    (master_doc, 'limis.tex', 'limis Documentation',
     'Philip Streck', 'manual'),
]

man_pages = [
    (master_doc, 'limis', 'limis Documentation',
     [author], 1)
]

texinfo_documents = [
    (master_doc, 'limis', 'limis Documentation',
     author, 'limis', 'One line description of project.',
     'Miscellaneous'),
]

epub_title = project
epub_exclude_files = ['search.html']

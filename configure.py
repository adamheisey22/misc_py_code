# Configuration file for the Sphinx documentation builder.

# -- Project information -----------------------------------------------------

project = 'Your Project Title'
author = 'Your Name or Organization'
release = '1.0'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.todo',
    'sphinx.ext.mathjax',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'

# -- Options for LaTeX output ------------------------------------------------

latex_engine = 'pdflatex'
latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    'preamble': r'''
        \usepackage{amsmath,amsfonts,amssymb,amsthm}
        \usepackage{graphicx}
        \usepackage{times}
        \usepackage{babel}
        \usepackage{booktabs}
        \usepackage{tabulary}
        \usepackage{url}
        ''',

    # Latex figure (float) alignment
    'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'YourProjectName.tex', 'Your Project Documentation',
     'Your Name or Organization', 'manual'),
]

# -- Extension configuration -------------------------------------------------

# If you have special requirements or need to further customize your LaTeX or HTML output,
# you may need to extend this configuration or directly modify the LaTeX templates.


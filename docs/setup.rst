.. _setup:

#####
Setup
#####

1. Clone the `repository <https://github.com/COMP523TeamD/HeadCircumferenceTool>`_.
2. :code:`pip install -r requirements.txt`

Start GUI
#########

You might need to run :code:`chmod +x gui.py`.

.. code-block:: text

    usage: ./gui.py [-h] [-d] [-s] [-e] [-f] [-t THEME] [-c COLOR]

    options:
      -h, --help            show this help message and exit
      -d, --debug           print debug info
      -s, --smooth          smooth image before rendering
      -e, --export-index    exported filenames will use the index displayed in the GUI instead of the original image name
      -f, --full-path       image status bar will show full path
      -t THEME, --theme THEME
                            configure theme, options are light-hct, dark-hct, light, dark, and the default theme is dark-hct
      -c COLOR, --color COLOR
                            contour color as name (e.g. red) or hex color code rrggbb

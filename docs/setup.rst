#####
Setup
#####

:Date: |today|

1. Clone the `repository <https://github.com/COMP523TeamD/HeadCircumferenceTool>`_.
2. :code:`pip install -r requirements.txt`

Start GUI
#########

.. code-block:: text

    usage: python -m [-h] [-d] [-s] [-e] [-f] [-t THEME] [-c COLOR] src.GUI.main
    
    options:
      -h, --help            show this help message and exit
      -d, --debug           print debug info
      -s, --smooth          smooth image before rendering
      -e, --export-index    exported filenames will use the index displayed in the
                            GUI instead of the original image name
      -f, --full-path       image status bar will show full path
      -t THEME, --theme THEME
                            configure theme, options are light, dark-hct, dark,
                            light-hct; default theme is dark-hct
      -c COLOR, --color COLOR
                            contour color as name (e.g. red) or hex color code
                            rrggbb

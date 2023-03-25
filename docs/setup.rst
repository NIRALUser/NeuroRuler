.. _setup:

#####
Setup
#####

1. Clone the `repository <https://github.com/COMP523TeamD/HeadCircumferenceTool>`_.
2. :code:`pip install -r requirements.txt`

Start GUI
#########

Current working directory must be `.../HeadCircumferenceTool`.

Windows users can double-click on `gui.pyw` to start the application.

For any OS, the following will work, though you may need to run `chmod +x gui.py`:

.. code-block:: text
    usage: ./gui.py [-h] [-d] [-s] [-e] [-t THEME] [-c COLOR]

    options:
      -h, --help            show this help message and exit
      -d, --debug           print debug info
      -s, --smooth          smooth image before rendering
      -e, --export-index    exported filenames will use the index displayed in the GUI instead of the original image name
      -t THEME, --theme THEME
                            configure theme, options are dark, dark-hct, light, light-hct, and the default theme is dark-hct
      -c COLOR, --color COLOR
                            contour color as name (e.g. red) or hex color code rrggbb

![Tests](https://github.com/COMP523TeamD/HeadCircumferenceTool/actions/workflows/tests.yml/badge.svg)

# Head Circumference Tool

> A program that allows you to calculate head circumference from MRI (`.nii`, `.nii.gz`, `.nrrd`) data.

We are currently working on the GUI and confirming that our circumference measurement results are correct using pre-computed data.

## Setup

1. Clone the repository
2. `pip install -r requirements.txt`

## Start GUI

```
usage: python -m [-h] [-d] [-s] [-e] [-f] [-t THEME] [-c COLOR] src.GUI.main

options:
  -h, --help            show this help message and exit
  -d, --debug           print debug info
  -s, --smooth          smooth image before rendering
  -e, --export-index    exported filenames will use the index displayed in the GUI
  -f, --full-path       image status bar will show full path
  -t THEME, --theme THEME
                        configure theme, options are dark-hct, light-hct, dark, light
  -c COLOR, --color COLOR
                        contour color as name (e.g. red) or hex rrggbb
```

## Documentation

- [https://headcircumferencetool.readthedocs.io](https://headcircumferencetool.readthedocs.io)

## Run tests

- `pytest`

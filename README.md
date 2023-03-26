
# Head Circumference Tool

![Tests](https://github.com/COMP523TeamD/HeadCircumferenceTool/actions/workflows/tests.yml/badge.svg)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)(https://github.com/psf/black)
![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)

> A program that allows you to calculate head circumference from MRI (`.nii`, `.nii.gz`, `.nrrd`) data.

We are currently working on the algorithm and confirming that our circumference measurement results are correct.

## Setup

1. Clone the repository
2. `pip install -r requirements.txt`

## Start GUI

Current working directory must be `.../HeadCircumferenceTool`.

Windows users can double-click on `gui.pyw` to start the application.

For any OS, the following will work, though you may need to run `chmod +x gui.py` on macOS/Linux:

```text
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
```

## Configure settings

Edit [config.json](config.json). CLI arguments override what's there.

## Run tests

`pytest`

## Documentation

[https://headcircumferencetool.readthedocs.io](https://headcircumferencetool.readthedocs.io)

## Autoformat

`black .`

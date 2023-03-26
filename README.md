
# Head Circumference Tool

![Tests](https://github.com/COMP523TeamD/HeadCircumferenceTool/actions/workflows/tests.yml/badge.svg)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)
![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)

> A program that allows you to calculate head circumference from MRI (`.nii`, `.nii.gz`, `.nrrd`) data.

We are currently working on the algorithm and GUI.

## Setup

```text
git clone https://github.com/COMP523TeamD/HeadCircumferenceTool.git
cd HeadCircumferenceTool
pip install -r requirements.txt
```

## Start GUI

Windows users can double-click on `gui.pyw` to start the application.

On any OS, you can start the GUI by running the `gui.py` script. Your current working directory should be
`.../HeadCircumferenceTool`. You may need to run `chmod +x gui.py`.

```text
./gui.py
```

## Configure settings

Edit [`config.json`](config.json).

You can also supply CLI arguments, which override settings in `config.json`.

```text
usage: ./gui.py [-h] [-d] [-s] [-e] [-t THEME] [-c COLOR]

options:
  -h, --help            show this help message and exit
  -d, --debug           print debug info
  -s, --smooth          smooth image before rendering
  -e, --export-index    exported filenames will use the index displayed in the GUI instead of the original image name
  -t THEME, --theme THEME
                        configure theme, options are dark, dark-hct, light, or light-hct, and the default theme is
                        dark-hct
  -c COLOR, --color COLOR
                        contour color as name (e.g. red) or hex color code rrggbb
```

## Run tests

```text
pytest
```

## Documentation

[https://headcircumferencetool.readthedocs.io](https://headcircumferencetool.readthedocs.io)

## Autoformat

```text
black .
```

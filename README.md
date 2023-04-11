# Head Circumference Tool

![Tests](https://github.com/COMP523TeamD/HeadCircumferenceTool/actions/workflows/tests.yml/badge.svg)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)
![Python](https://img.shields.io/badge/python-3670A0?style=plastic&logo=python&logoColor=ffdd54)

> A program that calculates head circumference from MRI data (`.nii`, `.nii.gz`, `.nrrd`).

We are currently working on the algorithm and GUI.

## Cite this tool

If you want ;) format is bibtex.

```bibtex
@online{hct,
  title={Head Circumference Tool},
  author={Wei, Jesse and Lester, Madison and He, Peifeng and Schneider, Eric and Styner, Martin},
  url={https://github.com/COMP523TeamD/HeadCircumferenceTool}
}
```

## Setup

Your Python version needs to be 3.8+. Check with `python --version`. Then run these commands.

```text
git clone https://github.com/COMP523TeamD/HeadCircumferenceTool.git
cd HeadCircumferenceTool
pip install -r requirements.txt
```

## Start GUI

Windows users can double-click on `gui.pyw` to start the application. Or if that doesn't work, just enter `python gui.py` in Windows Terminal.

On any OS, you can start the GUI by running `./gui.py`.

Your current working directory should be `.../HeadCircumferenceTool`.
You may need to run `chmod +x gui.py`.

## Configure settings

Edit [`config.json`](config.json).

You can also supply CLI arguments, which override settings in `config.json`.

```text
usage: ./gui.py [-h] [-d] [-s] [-e] [-t THEME] [-c COLOR]

options:
  -h, --help            show this help message and exit
  -d, --debug           print debug info
  -s, --smooth          smooth image before rendering
  -e, --export-index    exported file names use the index displayed in the GUI
                        instead of the original file name
  -t THEME, --theme THEME
                        configure theme, options are dark, dark-green, dark-
                        hct, dark-purple, light, light-green, light-hct, or
                        light-purple
  -c COLOR, --color COLOR
                        contour color as name (e.g. red) or hex color code
                        rrggbb
```

## Run tests

`pytest`

## Documentation

[https://headcircumferencetool.readthedocs.io](https://headcircumferencetool.readthedocs.io)

## Autoformat code

`black .`

This will be run automatically before each commit.

## Modify pre-commit git hook

Edit [`.pre-commit-config.yaml`](.pre-commit-config.yaml).

Then run `pre-commit install`.

More instructions [here](https://pre-commit.com).

Do not name any source code files `ui_mainwindow.py|stylesheet.qss|resources.py|gui|gui.pyw`.
These files are ignored in [`.pre-commit-config.yaml`](.pre-commit-config.yaml).

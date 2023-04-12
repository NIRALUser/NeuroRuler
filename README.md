# Head Circumference Tool

![Tests](https://github.com/COMP523TeamD/HeadCircumferenceTool/actions/workflows/tests.yml/badge.svg)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)
![Python](https://img.shields.io/badge/python-3670A0?style=plastic&logo=python&logoColor=ffdd54)

> A program that calculates head circumference from MRI data (`.nii`, `.nii.gz`, `.nrrd`).

<p align="center">
  <img src="docs/_static/hct_demo.gif" alt="Head Circumference Tool GUI demo"/>
</p>

## Cite this tool

If you want 😉 format is bibtex.

```bibtex
@misc{hct,
  title={Head Circumference Tool},
  author={Wei, Jesse and Lester, Madison and He, Peifeng and Schneider, Eric and Styner, Martin},
  howpublished={\url{https://github.com/COMP523TeamD/HeadCircumferenceTool}},
  year={2023}
}
```

## Setup

Your Python version needs to be 3.8+. Check with `python --version`. If that doesn't work, you need to [install Python](https://www.python.org), and make sure to add it to `PATH`.

You will also need [git](https://git-scm.com), and make sure to add git to `PATH` too.

Then run these commands in your terminal.

```text
git clone https://github.com/COMP523TeamD/HeadCircumferenceTool.git
cd HeadCircumferenceTool
pip install -r requirements.txt
```

## Start GUI

Your current working directory needs to be `.../HeadCircumferenceTool`.

macOS/Linux users can start the GUI by running `./gui.py`. You may need to run `chmod +x gui.py`.

Windows users can double-click on `gui.pyw` to start the application. If that doesn't work, run `python gui.py` in Windows Terminal.

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

This will be run automatically before each commit due to our [pre-commit git hook](.pre-commit-config.yaml).

Don't name any source code files `stylesheet.qss|resources.py|gui.py|gui.pyw`.
These files are excluded from auto-formatting.

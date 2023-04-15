# Head Circumference Tool

![Tests](https://github.com/COMP523TeamD/HeadCircumferenceTool/actions/workflows/tests.yml/badge.svg)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)
![Python](https://img.shields.io/badge/python-3670A0?style=plastic&logo=python&logoColor=ffdd54)

> A program that calculates head circumference from MRI data (`.nii`, `.nii.gz`, `.nrrd`).

<p align="center">
  <img src="https://i.imgur.com/nqwqHq8.gif" alt="GUI demo"/>
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

## Install

Your Python version needs to be 3.8+. Check with `python --version`. Clone this repo, and install the Python dependencies.

```text
pip install -r requirements.txt
pip install -i https://test.pypi.org/simple/ NeuroRuler==0.4
```

If `pip` doesn't work, try `pip3` or `python3 -m pip`.

If contributing to this repo, please also run `pre-commit install` to run pre-commit actions (i.e., autoformat) on your code before commits.

## Start GUI

Run these commands in a Python terminal:

```text
from GUI import gui
gui()
```

Note: If you make changes to the repo, then use the [`gui.py`](https://github.com/COMP523TeamD/HeadCircumferenceTool/blob/main/gui.py) script to run the GUI. Changes you make will not be reflected in the package from pip until uploaded to PyPi.

## Configure settings

Edit [`config.json`](config.json).

You can also supply CLI arguments, which override settings in `config.json`.

```text
usage: gui.py [-h] [-d] [-e] [-t THEME] [-c COLOR]

options:
  -h, --help            show this help message and exit
  -d, --debug           print debug info
  -e, --export-index    exported file names use the index displayed in the GUI instead of the original file name
  -t THEME, --theme THEME
                        configure theme, options are dark, dark-green, dark-hct, dark-purple, light, light-green, light-hct, or
                        light-purple
  -c COLOR, --color COLOR
                        contour color as name (e.g. red) or hex color code rrggbb
```

## Run tests

`pytest`

## Documentation

[https://headcircumferencetool.readthedocs.io](https://headcircumferencetool.readthedocs.io)

See [`.readthedocs.yaml`](.readthedocs.yaml) and [`docs/`](docs/).

## Pre-commit actions

Run `pre-commit install` to enable pre-commit actions.

Before each commit, the actions in [`.pre-commit-config.yaml`](.pre-commit-config.yaml) will be run. Specifically, code will be reformatted with `black`. Note that some file names are excluded, so don't name any source code files those names.

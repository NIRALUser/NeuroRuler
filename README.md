# NeuroRuler

![Tests](https://github.com/COMP523TeamD/NeuroRuler/actions/workflows/tests.yml/badge.svg)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)
![Python](https://img.shields.io/badge/python-3670A0?style=plastic&logo=python&logoColor=ffdd54)

> A program that calculates head circumference from MRI data (`.nii`, `.nii.gz`, `.nrrd`).

<p align="center">
  <img src="https://i.imgur.com/nqwqHq8.gif" alt="GUI demo"/>
</p>

## Cite this tool

If you want 😉 format is bibtex.

```bibtex
@misc{neuroruler,
  title={NeuroRuler},
  author={Wei, Jesse and Lester, Madison and He, Peifeng and Schneider, Eric and Styner, Martin},
  howpublished={\url{https://github.com/COMP523TeamD/NeuroRuler}},
  year={2023}
}
```

## Install

Your Python version needs to be 3.8+. Check with `python --version`. Install via pip.

```sh
pip install NeuroRuler
```

If `pip` doesn't work, try `pip3` or `python3 -m pip`.

If contributing to this repo, please also run `pip install -r requirements.txt` to install additional development dependencies (e.g., formatting, documentation, etc.). After installing additional dependencies, run `pre-commit install` to enable pre-commit actions.

## Run GUI

Run these commands in a Python terminal:

```py
from NeuroRuler.GUI import gui

gui()
```

Note: If you make changes to the repo, then use the [`gui.py`](gui.py) script to run the GUI. Changes you make will not be reflected in the package from pip until uploaded to PyPI.

See [release](#release) for how to upload to PyPI or Test PyPI.

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

[https://NeuroRuler.readthedocs.io](https://NeuroRuler.readthedocs.io)

See [`.readthedocs.yaml`](.readthedocs.yaml) and [`docs/`](docs/).

## Pre-commit actions

Run `pre-commit install` to enable pre-commit actions.

Before each commit, the actions in [`.pre-commit-config.yaml`](.pre-commit-config.yaml) will be run. Specifically, code will be reformatted with `black`. Note that some file names are excluded, so don't name any source code files those names.

## Release

* [PyPI page](https://pypi.org/project/NeuroRuler/)
* [TestPyPI page](https://test.pypi.org/project/NeuroRuler/)

To publish to [PyPI](https://pypi.org/project/NeuroRuler/), edit the version number in [`setup.py`](setup.py). Then create a branch named `release-pypi/version-num`. Push a tagged (use the version number) commit to that branch to run the `pypi.yml` action, which will publish to PyPI.

The version number on PyPI will be the one in `setup.py`, so make sure it's correct!

Follow a similar process to publish to TestPyPI.

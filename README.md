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

Your Python version needs to be 3.8+. Check with `python --version`. Install with pip.

```sh
pip install NeuroRuler
```

If `pip` doesn't work, try `pip3`.

If contributing to this repo, run `pip install -r requirements.txt` to install additional development dependencies (for code formatting, documentation, etc.). After installing additional dependencies, run `pre-commit install` to enable pre-commit actions.

## Run GUI

Run these commands in a Python terminal:

```py
from NeuroRuler.GUI import gui
gui()
```

Note: If you make changes to the repo, use the [gui.py](https://github.com/COMP523TeamD/NeuroRuler/blob/main/gui.py) script to run the GUI. Changes you make will not be reflected in the package from pip until uploaded to PyPI.

## Configure settings

Edit the JSON configuration files [cli_config.json](https://github.com/COMP523TeamD/NeuroRuler/blob/main/cli_config.json) and [gui_config.json](https://github.com/COMP523TeamD/NeuroRuler/blob/main/gui_config.json).

You can also supply CLI arguments to the [gui.py](https://github.com/COMP523TeamD/NeuroRuler/blob/main/cli_config.json) script, which will override settings in [gui_config.json](https://github.com/COMP523TeamD/NeuroRuler/blob/main/cli_config.json).

Apply the `-h` command-line option when running those scripts to see the list of options.

## Run tests

For local testing, run `pytest`.

Our unit tests run on GitHub Actions on push and PR. If the image below says "passing," then the tests are passing.

![Tests](https://github.com/COMP523TeamD/NeuroRuler/actions/workflows/tests.yml/badge.svg)

**Note**: The tests in [tests/imports_GUI](https://github.com/COMP523TeamD/NeuroRuler/tree/main/tests/imports_GUI) are ignored during CI tests (see [tox.ini](https://github.com/COMP523TeamD/NeuroRuler/blob/main/tox.ini)) because in GitHub Actions causes a "libEGL.so not found" error (likely because the computers running the tests don't have monitors). These tests should be run locally only.

## Documentation

[https://NeuroRuler.readthedocs.io](https://NeuroRuler.readthedocs.io)

See [`.readthedocs.yaml`](https://github.com/COMP523TeamD/NeuroRuler/blob/main/.readthedocs.yaml) and [`docs/`](https://github.com/COMP523TeamD/NeuroRuler/tree/main/docs) to contribute.

## Pre-commit actions

Run `pre-commit install` to enable pre-commit actions.

Before each commit, the actions in [`.pre-commit-config.yaml`](https://github.com/COMP523TeamD/NeuroRuler/blob/main/.pre-commit-config.yaml) will be run. Specifically, code will be reformatted with `black`.

**Note**: Some file names are excluded, so don't name any source code files those names.

## Release

To test the package locally before releasing, run these commands from the `NeuroRuler` directory.

```sh
rm -r dist/
pip uninstall NeuroRuler
python setup.py sdist
pip install dist/*.tar.gz
cd ..
```

The `cd docs` is there because you should test imports from a directory that isn't `NeuroRuler`.

To publish to [PyPI](https://pypi.org/project/NeuroRuler/), edit the version number in [setup.py](https://github.com/COMP523TeamD/NeuroRuler/blob/main/setup.py). Then push to a branch called `release-pypi` (create it if it doesn't exist). This will trigger [pypi.yml](https://github.com/COMP523TeamD/NeuroRuler/blob/main/.github/workflows/pypi.yml).

To publish on Test PyPI, do the same as above, but push to a branch called `release-testpypi`.

# NeuroRuler <span><img width="20" src="https://i.imgur.com/pYlhHqu.png"></span>

![Tests](https://github.com/NIRALUser/NeuroRuler/actions/workflows/tests.yml/badge.svg)
![Documentation](https://readthedocs.org/projects/neuroruler/badge/?version=latest)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)
![Python](https://img.shields.io/badge/python-3670A0?style=plastic&logo=python&logoColor=ffdd54)

NeuroRuler is a program that calculates head circumference from MRI data (`.nii`, `.nii.gz`, `.nrrd`).

<p align="center">
  <img src="https://i.imgur.com/nqwqHq8.gif" alt="GUI demo"/>
</p>

<p align="center">
  <a href="https://www.youtube.com/watch?v=ZhSg5xwzbmo"><img src="https://img.youtube.com/vi/ZhSg5xwzbmo/0.jpg" alt="full demo video"></a>
</p>

<p align="center">
  <a href="https://www.youtube.com/watch?v=ZhSg5xwzbmo">Full demo</a>
</p>

## Cite this tool

If you want 😉 format is bibtex.

```bibtex
@misc{neuroruler,
  title={NeuroRuler},
  author={Wei, Jesse and Lester, Madison and He, Peifeng and Schneider, Eric and Styner, Martin},
  howpublished={\url{https://github.com/NIRALUser/NeuroRuler}},
  year={2023}
}
```

## Install

Your Python version needs to be 3.8+. Check with `python --version`. Install with pip.

```sh
pip install NeuroRuler
```

If `pip` doesn't work, try `pip3`.

If contributing to this repo, clone/fork and run `pip install -r requirements.txt` to install additional development dependencies (for code formatting, documentation, etc.). After installing additional dependencies, run `pre-commit install` to enable pre-commit actions.

## Run GUI

Run these commands in a Python terminal:

```py
from NeuroRuler.GUI import gui
gui()
```

Note: If you make changes to the repo, use the [gui.py](https://github.com/NIRALUser/NeuroRuler/blob/main/gui.py) script to run the GUI. Changes you make will not be reflected in the pip package until uploaded to PyPI.

## Import/Export

In "circumference mode" (after clicking Apply), click Export to export JSON files containing the circumferences of all loaded images, along with the settings applied to each image.

You can then use File > Import MRI Settings to import a JSON file of this kind to load the same image with the same settings.

## Configure settings

After cloning the repo, edit the JSON configuration files [gui_config.json](https://github.com/NIRALUser/NeuroRuler/blob/main/gui_config.json) and [cli_config.json](https://github.com/NIRALUser/NeuroRuler/blob/main/cli_config.json).

You can also supply CLI arguments to the [gui.py](https://github.com/NIRALUser/NeuroRuler/blob/main/gui.py) or [cli.py](https://github.com/NIRALUser/NeuroRuler/blob/main/cli.py) scripts, which will override settings in the JSON configuration files.

Apply the `-h` command-line option when running those scripts to see the list of options. You can see some examples of CLI options in [test_cli.py](https://github.com/NIRALUser/NeuroRuler/blob/main/tests/test_cli.py).

## Run tests

To test locally, run `pytest`.

Our algorithm tests assert that our GUI calculations have at least a 0.98 R<sup>2</sup> value with ground truth data from the old Head Circumference Tool. Additionally, we test that our CLI and GUI produce the same results. Lastly, we verified that our circumference result is correct for images with non-(1.0, 1.0, 1.0) pixel spacing.

Our tests run on GitHub Actions on push and PR via `tox` ([tests.yml](https://github.com/NIRALUser/NeuroRuler/blob/main/.github/workflows/tests.yml)). If the image below says "passing," then the tests are passing.

<p align="center">
  <img src="https://github.com/NIRALUser/NeuroRuler/actions/workflows/tests.yml/badge.svg" alt="GitHub actions tests.yml badge"/>
</p>

## Documentation

[https://NeuroRuler.readthedocs.io](https://NeuroRuler.readthedocs.io)

See [.readthedocs.yaml](https://github.com/NIRALUser/NeuroRuler/blob/main/.readthedocs.yaml) and [docs/](https://github.com/NIRALUser/NeuroRuler/tree/main/docs) to contribute.

[Team website](https://tarheels.live/comp523teamd/)

## Pre-commit actions

Run `pre-commit install` to enable pre-commit actions.

Before each commit, the actions in [.pre-commit-config.yaml](https://github.com/NIRALUser/NeuroRuler/blob/main/.pre-commit-config.yaml) will be run. Specifically, code will be reformatted with `black`.

**Note**: Some file names are excluded, so don't name any source code files those names.

## Release

To test the package locally before releasing, use [scripts/testdist](scripts/testdist). If using macOS, run with `. scripts/testdist`. If using Windows, you may need to modify the script slightly.

You must test from a directory that isn't `NeuroRuler/`. If your directory is `NeuroRuler/`, then imports will import from the source code, not the package.

To publish to [PyPI](https://pypi.org/project/NeuroRuler/), edit the version number in [setup.py](https://github.com/NIRALUser/NeuroRuler/blob/main/setup.py). Then push to a branch called `release-pypi` (create it if it doesn't exist). This will trigger [pypi.yml](https://github.com/NIRALUser/NeuroRuler/blob/main/.github/workflows/pypi.yml), which will run tests and publish to PyPI if the tests pass.

To publish to [Test PyPI](https://test.pypi.org/project/NeuroRuler/), do the same as above, but push to a branch called `release-testpypi`.

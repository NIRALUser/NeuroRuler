[![tests GitHub action](https://github.com/NIRALUser/NeuroRuler/actions/workflows/tests.yml/badge.svg)](https://github.com/NIRALUser/NeuroRuler/actions/workflows/tests.yml)
[![documentation badge](https://readthedocs.org/projects/neuroruler/badge/?version=latest)](https://NeuroRuler.readthedocs.io/en/latest/)

# NeuroRuler

Cross-platform program that calculates head circumference from MRI data (`.nii`, `.nii.gz`, `.nrrd`).

<p align="center">
  <img src="https://i.imgur.com/cdtsrwD.gif" alt="GUI demo"/>
</p>

<p align="center">
  <a href="https://www.youtube.com/watch?v=ZhSg5xwzbmo"><img src="https://img.youtube.com/vi/ZhSg5xwzbmo/0.jpg" alt="full demo video"></a>
</p>

<p align="center">
  <a href="https://www.youtube.com/watch?v=ZhSg5xwzbmo">Demo</a>
</p>

The demo is slightly outdated, but most information is relevant.

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

If `python` or `pip` don't work, try `python3` and `pip3`.

## Usage

Download the latest [release](https://github.com/NIRALUser/NeuroRuler/releases).

The [gui.py](https://github.com/NIRALUser/NeuroRuler/blob/main/gui.py) and [cli.py](https://github.com/NIRALUser/NeuroRuler/blob/main/cli.py) scripts are entry points for NeuroRuler's GUI and CLI.

[gui_config.json](https://github.com/NIRALUser/NeuroRuler/blob/main/gui_config.json) and [cli_config.json](https://github.com/NIRALUser/NeuroRuler/blob/main/cli_config.json) set default settings for the GUI and CLI. For more information, see [Configure default settings](#configure-default-settings).

## For developers

Developers contributing to the repository should clone the repository. `gui.py` and `cli.py` will then import from the local repository and reflect changes made to the codebase.

Developers should also run `pip install -r requirements.txt` to install additional development dependencies and `pre-commit install` to install pre-commit git hooks.

**Note**: Cloning (but not installing via pip) will use ~2G because of the large data files in [data/](https://github.com/NIRALUser/NeuroRuler/tree/main/data) used in our unit tests.

To improve this, please see [issue #93](https://github.com/NIRALUser/NeuroRuler/issues/93).

## Run GUI

```sh
python gui.py
```

Run `python gui.py -h` to see command-line options.

The GUI can also be run from any directory from a Python terminal. After opening a Python terminal, run these commands:

```py
from NeuroRuler.GUI import gui
gui()
```

<p align="center">Same as the code in <code>gui.py</code></p>

## Run CLI

```text
python cli.py <file>
```

See [test_cli.py](https://github.com/NIRALUser/NeuroRuler/blob/main/tests/test_cli.py) for example usages. Note that the CLI script accepts only one file at a time because it's expected that you'll use a shell script to loop over multiple files.

```text
usage: cli.py [-h] [-d] [-r] [-x X] [-y Y] [-z Z] [-s SLICE] [-c CONDUCTANCE] [-i ITERATIONS] [-t STEP] [-f FILTER] [-l LOWER]
              [-u UPPER]
              file

A program that calculates head circumference from MRI data (``.nii``, ``.nii.gz``, ``.nrrd``).

positional arguments:
  file                  file to compute circumference from, file format must be *.nii.gz, *.nii, or *.nrrd

options:
  -h, --help            show this help message and exit
  -d, --debug           print debug info
  -r, --raw             print just the "raw" circumference
  -x X, --x X           x rotation (in degrees)
  -y Y, --y Y           y rotation (in degrees)
  -z Z, --z Z           z rotation (in degrees)
  -s SLICE, --slice SLICE
                        slice (Z slice, 0-indexed)
  -c CONDUCTANCE, --conductance CONDUCTANCE
                        conductance smoothing parameter
  -i ITERATIONS, --iterations ITERATIONS
                        smoothing iterations
  -t STEP, --step STEP  time step (smoothing parameter)
  -f FILTER, --filter FILTER
                        which filter to use (Otsu or binary), default is Otsu
  -l LOWER, --lower LOWER
                        lower threshold for binary threshold
  -u UPPER, --upper UPPER
                        upper threshold for binary threshold
```

<p align="center">Output of <code>python cli.py -h</code> (could be outdated)</p>

## Import/export image settings JSON

In the GUI's "circumference mode" (after clicking Apply), click the large Export button under the image to export image settings JSON file(s) containing the circumferences of all loaded images and the settings applied to each image.

You can then use File > Import Image Settings to import an image settings JSON to load the same image with the same settings.

Here is an example:

```py
{
    "input_image_path": "/Users/jesse/Documents/GitHub/COMP523/NeuroRuler/data/MicroBiome_1month_T1w.nii.gz",
    "output_contoured_slice_path": "/Users/jesse/Documents/GitHub/COMP523/NeuroRuler/output/MicroBiome_1month_T1w/MicroBiome_1month_T1w_contoured.png",
    "circumference": 285.04478394448125,
    "x_rotation": -17,
    "y_rotation": -18,
    "z_rotation": 24,
    "slice": 131,
    "smoothing_conductance": 4.0,
    "smoothing_iterations": 10,
    "smoothing_time_step": 0.08,
    "threshold_filter": "Otsu"
}
```

When multiple images are exported, the output directory structure looks like this:

```text
output
├── 150649_V06_t1w
│   ├── 150649_V06_t1w_contoured.png
│   └── 150649_V06_t1w_settings.json
└── MicroBiome_1month_T1w
    ├── MicroBiome_1month_T1w_contoured.png
    └── MicroBiome_1month_T1w_settings.json
```

## Configure default settings

Edit the JSON configuration files [gui_config.json](https://github.com/NIRALUser/NeuroRuler/blob/main/gui_config.json) and [cli_config.json](https://github.com/NIRALUser/NeuroRuler/blob/main/cli_config.json). `gui.py` and `cli.py` will create these files if they don't exist.

Command-line arguments supplied to the [gui.py](https://github.com/NIRALUser/NeuroRuler/blob/main/gui.py) or [cli.py](https://github.com/NIRALUser/NeuroRuler/blob/main/cli.py) scripts override settings in the JSON configuration files. JSON settings are default values for the GUI and CLI: If a setting in the JSON file is not overriden by a CLI argument, the JSON file setting will be used.

## Run tests

To test locally, run `pytest`.

Our algorithm tests assert that our GUI calculations have at least a 0.98 R<sup>2</sup> value with ground truth data from the old Head Circumference Tool (the `.tsv` files in `data/`). In all unit tests, we calculate circumference from the middle axial slice with all rotation values set to 0. Also, we use the default smoothing parameters and Otsu threshold.

We use a similar R<sup>2</sup> test to verify that our circumference result is correct for images with non-(1.0, 1.0, 1.0) pixel spacing. We verified manually (no unit test) that the GUI computes similar circumferences for (a, b, c) pixel spacing images generated from (1.0, 1.0, 1.0) pixel spacing images.

To test CLI, we test that our CLI produces the same results as the GUI.

Our tests run on GitHub Actions on push and PR via `tox` ([tests.yml](https://github.com/NIRALUser/NeuroRuler/blob/main/.github/workflows/tests.yml)). If the image below says "passing," then the tests are passing.

<p align="center">
  <a href="https://github.com/NIRALUser/NeuroRuler/actions/workflows/tests.yml">
  <img src="https://github.com/NIRALUser/NeuroRuler/actions/workflows/tests.yml/badge.svg" alt="GitHub actions tests.yml badge"/>
  </a>
</p>

## Documentation

[https://NeuroRuler.readthedocs.io](https://NeuroRuler.readthedocs.io)

See [.readthedocs.yaml](https://github.com/NIRALUser/NeuroRuler/blob/main/.readthedocs.yaml) and [docs/](https://github.com/NIRALUser/NeuroRuler/tree/main/docs) to contribute.

[Team website](https://tarheels.live/comp523teamd/)

## Release

To test the package locally before releasing on PyPI, use the [testdist](https://github.com/NIRALUser/NeuroRuler/blob/main/testdist) script. If using macOS, run with `. ./testdist`. If using Windows, you may need to modify the script slightly.

You should test from a directory that isn't `NeuroRuler/`. If your directory is `NeuroRuler/`, then imports will import from the source code, not the package.

To publish to [PyPI](https://pypi.org/project/NeuroRuler/), edit the version number in [setup.py](https://github.com/NIRALUser/NeuroRuler/blob/main/setup.py). Then push to a branch called `release-pypi` (create it if it doesn't exist). This will trigger [pypi.yml](https://github.com/NIRALUser/NeuroRuler/blob/main/.github/workflows/pypi.yml), which will run tests and publish to PyPI if the tests pass.

To publish to [Test PyPI](https://test.pypi.org/project/NeuroRuler/), do the same as above, but push to a branch called `release-testpypi`.

If any of these files changes, they should be re-released on our GitHub release page: `gui.py`, `cli.py`, `gui_config.json`, `cli_config.json`.

Additionally, these files should be updated: `CITATION.cff`

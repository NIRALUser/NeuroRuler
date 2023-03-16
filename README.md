![Tests](https://github.com/COMP523TeamD/HeadCircumferenceTool/actions/workflows/tests.yml/badge.svg)

# Head Circumference Tool 

> A program that allows you to calculate head circumference from MRI (`.nii`, `.nii.gz`, `.nrrd`) data.

We are currently working on the GUI and confirming that our circumference measurement results are correct using pre-computed data.

## Setup

1. Clone the repository
2. Run `pip install -r requirements.txt`

## Start GUI

```
usage: python -m [-s] [-e] src.GUI.main

options:
  -h, --help          show this help message and exit
  -s, --smooth        smooth image before rendering (False by default)
  -e, --export_index  exported filenames will use the index displayed in the GUI

```

## Documentation

- In [doc/](https://github.com/COMP523TeamD/HeadCircumferenceTool/tree/main/doc).

## Run tests

- `pytest`

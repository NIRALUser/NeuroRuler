# Head Circumference Tool

![Tests](https://github.com/COMP523TeamD/HeadCircumferenceTool/actions/workflows/tests.yml/badge.svg)

> A program that allows you to calculate head circumference from MRI (`.nii`, `.nii.gz`, `.nrrd`) data.

We are currently working on the GUI and confirming that our circumference measurement results are correct using pre-computed data.

## Setup

1. Clone the repository.
2. Run `pip install -r requirements.txt`.

## Starting GUI

- `python -m src.GUI.main`.
- Apply `-j` or `-p` option to write JPG or PNG files, respectively, to `img/` for image rendering.
- Apply `-n` option to use `numpy` arrays only during image rendering (currently does not render most images correctly, also bugged after clicking Apply).
- If no flag is applied, the program writes JPG to `img/`.
- [Speed comparison between jpg and np only](https://youtu.be/GE80cbHEBy8)

## Running tests

- `pytest`

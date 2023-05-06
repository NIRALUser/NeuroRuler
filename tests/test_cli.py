"""Black box integration tests for the command line.

Hardcoded numbers were manually retrieved from the GUI calculations.

The tests in ``tests/imports_GUI`` confirm that the GUI calculations are correct. So if the CLI calculations
match those of the GUI, then the CLI calculations are correct."""

import subprocess
from subprocess import PIPE


def test_basic():
    command = "python cli.py data/IBIS_Case1_V06_t1w_RAI.nrrd"
    proc = subprocess.Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    assert (
        proc.stdout.read().rstrip()
        == b"Calculated Circumference: 433.436 millimeters (mm)"
    )


def test_slice_options():
    command = (
        "python cli.py --x=16 --y=2 --z=22 --slice=96 data/IBIS_Case1_V06_t1w_RAI.nrrd"
    )
    proc = subprocess.Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    assert (
        proc.stdout.read().rstrip()
        == b"Calculated Circumference: 421.511 millimeters (mm)"
    )


def test_binary():
    command = "python cli.py --slice=69 --lower=0.0 --upper=200.0 --filter=binary data/BCP_Dataset_2month_T1w.nrrd"
    proc = subprocess.Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    assert (
        proc.stdout.read().rstrip()
        == b"Calculated Circumference: 390.444 millimeters (mm)"
    )


def test_explicit_otsu():
    """Otsu is applied by default, but this tests for the explicit flag."""
    command = "python cli.py --filter=otsu data/IBIS_Dataset_NotAligned_6month_T1w.nrrd"
    proc = subprocess.Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    assert (
        proc.stdout.read().rstrip()
        == b"Calculated Circumference: 425.13 millimeters (mm)"
    )


def test_smoothing_options():
    command = "python cli.py --conductance=1.0 --iterations=20 --step=0.05 data/MicroBiome_1month_T1w.nii.gz"
    proc = subprocess.Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    assert (
        proc.stdout.read().rstrip()
        == b"Calculated Circumference: 365.712 millimeters (mm)"
    )

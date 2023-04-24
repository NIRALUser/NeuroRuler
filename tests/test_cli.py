"""Black box integration tests for the command line."""

import subprocess
from subprocess import PIPE


def test1():
    command = "python cli.py --otsu data/IBIS_Case1_V06_t1w_RAI.nrrd"
    proc = subprocess.Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
    assert proc.stdout.read().rstrip() == b"Calculated Circumference: 456.475 millimeters (mm)"


def test2():
    command = "python cli.py --x=16 --y=2 --z=22 --slice=96 --otsu data/IBIS_Case1_V06_t1w_RAI.nrrd"
    proc = subprocess.Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
    assert proc.stdout.read().rstrip() == b"Calculated Circumference: 440.96 millimeters (mm)"


def test3():
    command = "python cli.py --slice=69 --lower=0.0 --upper=200.0 data/BCP_Dataset_2month_T1w.nrrd"
    proc = subprocess.Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
    assert proc.stdout.read().rstrip() == b"Calculated Circumference: 410.777 millimeters (mm)"


def test4():
    command = "python cli.py --otsu data/IBIS_Dataset_NotAligned_6month_T1w.nrrd"
    proc = subprocess.Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
    assert proc.stdout.read().rstrip() == b"Calculated Circumference: 557.144 millimeters (mm)"


def test5():
    command = "python cli.py --conductance=1.0 --iterations=20 --step=0.05 --otsu data/MicroBiome_1month_T1w.nii.gz"
    proc = subprocess.Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
    assert proc.stdout.read().rstrip() == b"Calculated Circumference: 481.103 millimeters (mm)"

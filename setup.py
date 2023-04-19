# Source: https://github.com/hmeine/qimage2ndarray/blob/master/setup.py

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from pathlib import Path

install_requires: list[str] = [
    "setuptools",
    "SimpleITK",
    "numpy",
    "argparse",
    "opencv-python",
    "pytest",
    "PyQt6",
    "qimage2ndarray",
    "screeninfo",
]
"""All required (i.e., for functionality) dependencies that are installed when running `pip install NeuroRuler`.

Non-functional (e.g., formatting, documentation) dependencies listed in requirements.txt."""

setup(
    name="NeuroRuler",
    version="0.0.1",
    description="A program that calculates head circumference from MRI data (`.nii`, `.nii.gz`, `.nrrd`).",
    # Cannot use multiple authors
    # https://stackoverflow.com/questions/9999829/how-to-specify-multiple-authors-emails-in-setup-py
    author="COMP523 Team D",
    author_email="comp523d@gmail.com",
    url="https://github.com/COMP523TeamD/NeuroRuler",
    download_url="https://github.com/COMP523TeamD/NeuroRuler/releases",
    keywords=[
        "MRI",
        "NIfTI",
        "NRRD",
        "brain",
        "circumference",
        "PyQt6",
    ],
    install_requires=install_requires,
    # We don't need extras_require
    # See https://stackoverflow.com/questions/41268863/what-is-the-difference-between-extras-require-and-install-requires-in-se
    # extras_require=dict(),
    tests_require=install_requires + ["tox", "pytest", "pytest-cov"],
    # TODO: Change after refactoring
    packages=["NeuroRuler.GUI"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)

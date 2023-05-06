# Source: https://github.com/hmeine/qimage2ndarray/blob/master/setup.py

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

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
    # For current version number, see
    # https://pypi.org/project/NeuroRuler/
    version="1.0.0",
    description="A program that calculates head circumference from MRI data (`.nii`, `.nii.gz`, `.nrrd`).",
    # Cannot use multiple authors
    # https://stackoverflow.com/questions/9999829/how-to-specify-multiple-authors-emails-in-setup-py
    author="COMP523 Team D",
    author_email="comp523d@gmail.com",
    url="https://github.com/NIRALUser/NeuroRuler",
    download_url="https://github.com/NIRALUser/NeuroRuler/releases",
    keywords=[
        "MRI",
        "NIfTI",
        "NRRD",
        "brain",
        "circumference",
        "PyQt6",
    ],
    install_requires=install_requires,
    tests_require=install_requires + ["tox", "pytest", "pytest-cov"],
    # See https://setuptools.pypa.io/en/latest/userguide/package_discovery.html
    package_dir={"NeuroRuler": "NeuroRuler"},
    packages=find_packages(),
    package_data={
        "NeuroRuler": ["GUI/*.ui", "GUI/static/*", "GUI/themes/*/*", "../*.json"]
    },
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

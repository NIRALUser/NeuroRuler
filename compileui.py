#!/usr/bin/env python

"""This script runs a command that compiles the .ui file to a .py file.

Must be run from .../HeadCircumferenceTool

You must have PySide6 and the pyside6-uic command installed"""

import os
from src.utils.constants import UI_FILE_PATH, COMPILED_UI_FILE_PATH

os.system(f"pyside6-uic {UI_FILE_PATH} > {COMPILED_UI_FILE_PATH}")

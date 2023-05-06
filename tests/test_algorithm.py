"""Test algorithm by computing R^2 from GUI calculation and ground truth data.

Simulates GUI button clicks.

Uses GUI. GUI imports and tests will not run in CI. See note in tests/README.md."""

from tests.constants import (
    TARGET_R_SQUARED,
    labeled_result,
    UBUNTU_GITHUB_ACTIONS_CI,
    compute_r_squared,
)
import re
import os
import sys
import os
import pytest
from pathlib import Path
from typing import Union
import SimpleITK as sitk
import numpy as np

if not UBUNTU_GITHUB_ACTIONS_CI:
    from PyQt6.QtTest import QTest
    from PyQt6.QtWidgets import (
        QPushButton,
        QApplication,
    )
    from PyQt6.uic.load_ui import loadUi
    from PyQt6.QtCore import Qt, QSize
    from NeuroRuler.utils.img_helpers import *
    from NeuroRuler.GUI.main import *
    import NeuroRuler.utils.global_vars as global_vars
    from NeuroRuler.utils.constants import View, ThresholdFilter
    import NeuroRuler.utils.constants as constants

    # Note, do not use imports like
    # from NeuroRuler.utils.global_vars import IMAGE_DICT
    # This would make the global variables not work
    import NeuroRuler.utils.global_vars as global_vars
    import NeuroRuler.utils.imgproc as imgproc
    import NeuroRuler.utils.gui_settings as gui_settings


@pytest.mark.skipif(
    UBUNTU_GITHUB_ACTIONS_CI, reason="No GUI on Ubuntu GitHub Actions CI environment"
)
def calculate_circumference(path) -> float:
    # Set up UI
    app = QApplication(sys.argv)
    window = MainWindow()

    # Load in image
    window.browse_files(False, path)
    window.set_view_z()
    window.orient_curr_image()
    window.toggle_setting_to_false()
    gui_settings.CONTOUR_COLOR = "b55162"
    binary_contour_slice: np.ndarray = window.render_curr_slice()
    return window.render_circumference(binary_contour_slice)


@pytest.mark.skipif(
    UBUNTU_GITHUB_ACTIONS_CI, reason="No GUI on Ubuntu GitHub Actions CI environment"
)
def test_algorithm():
    labeled_data = []
    calculated_data = []
    data_folder = "data"

    length = 0

    for file_name in os.listdir(data_folder):
        if file_name.endswith("w.nrrd"):
            nrrd_prefix = os.path.splitext(file_name)[0][
                :10
            ]  # Remove the file extension to get the prefix
            for tsv_file_name in os.listdir(data_folder):
                if nrrd_prefix in tsv_file_name and tsv_file_name.endswith(".tsv"):
                    length = length + 1
                    labeled_data.append(
                        labeled_result(data_folder + "/" + tsv_file_name)
                    )
                    calculated_data.append(
                        calculate_circumference(data_folder + "/" + file_name)
                    )
                    break
            else:
                continue

    assert length > 20
    assert compute_r_squared(labeled_data, calculated_data) > TARGET_R_SQUARED

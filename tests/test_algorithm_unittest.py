"""Test algorithm by computing R^2 from GUI calculation and ground truth data.

Simulates GUI button clicks.

Uses GUI. GUI imports and tests will not run in CI. See note in tests/README.md."""

from tests.constants import (
    TARGET_R_SQUARED,
    labeled_result,
    UBUNTU_GITHUB_ACTIONS_CI,
    compute_r_squared,
)
import os
import sys
import unittest
import pytest

if not UBUNTU_GITHUB_ACTIONS_CI:
    from PyQt6.QtWidgets import QApplication, QPushButton
    from PyQt6.QtTest import QTest
    from PyQt6.QtCore import Qt
    from NeuroRuler.utils.img_helpers import *
    from NeuroRuler.GUI.main import *


class MainWindowTest(unittest.TestCase):
    """Test the program by simulating GUI actions."""

    @unittest.skipIf(
        UBUNTU_GITHUB_ACTIONS_CI,
        reason="No GUI on Ubuntu GitHub Actions CI environment",
    )
    def test_alg(self):
        app = QApplication(sys.argv)
        self.form = (
            MainWindow()
        )  # Pass the local parent object to the child constructor

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

                        # Get labeled data
                        labeled_data.append(
                            labeled_result(data_folder + "/" + tsv_file_name)
                        )

                        # Simulate GUI actions
                        self.form.browse_files(False, data_folder + "/" + file_name)
                        self.form.toggle_setting_to_true()
                        button = QPushButton("apply")
                        button.clicked.connect(self.form.settings_export_view_toggle)
                        button.click()

                        # Get circumference
                        circumference_label: str = self.form.circumference_label
                        split_parts = circumference_label.text().split(":")
                        part_after_colon = split_parts[-1].strip()[:3]
                        calculated_data.append(float(part_after_colon))
                        break
                else:
                    continue

        self.assertTrue(length > 10)
        self.assertTrue(
            compute_r_squared(labeled_data, calculated_data) > TARGET_R_SQUARED
        )

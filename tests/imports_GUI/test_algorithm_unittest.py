import os

import sys
import unittest

import pytest

from NeuroRuler.utils.img_helpers import *
from NeuroRuler.GUI.main import *

from PyQt6.QtWidgets import QApplication, QPushButton
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt


class MainWindowTest(unittest.TestCase):
    """Test the program by simulating GUI actions"""

    def test_alg(self):
        app = QApplication(sys.argv)
        self.form = (
            MainWindow()
        )  # pass the local parent object to the child constructor

        labeled_data = []
        calculated_data = []
        data_folder = "data"

        length = 0

        for file_name in os.listdir(data_folder):
            if file_name.endswith("w.nrrd"):
                nrrd_prefix = os.path.splitext(file_name)[0][
                    :10
                ]  # remove the file extension to get the prefix
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

                        # Get Circumference
                        circumference_label: str = self.form.circumference_label
                        split_parts = circumference_label.text().split(":")
                        part_after_colon = split_parts[-1].strip()[:3]
                        calculated_data.append(float(part_after_colon))
                        break
                else:
                    continue

        # Calculate R^2
        r_square = np.corrcoef(labeled_data, calculated_data)[0, 1]
        self.assertTrue(length > 10)
        self.assertTrue(r_square**2 > 0.98)


def labeled_result(path) -> float:
    with open(path, "r") as file:
        line = file.readline().strip()
        parts = line.split("\t")
        last_section = parts[-1]
        return float(last_section)

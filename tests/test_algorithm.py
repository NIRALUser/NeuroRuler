import re
from NeuroRuler.utils.img_helpers import *
from NeuroRuler.GUI.main import *
import NeuroRuler.utils.global_vars as global_vars
import sys
import os
from pathlib import Path
from typing import Union

import SimpleITK as sitk
import numpy as np

from PyQt6 import QtGui, QtCore
from PyQt6.QtGui import QPixmap, QAction, QImage, QIcon, QResizeEvent
from PyQt6.QtWidgets import (
    QPushButton,
    QApplication,
)
from PyQt6.uic.load_ui import loadUi
from PyQt6.QtCore import Qt, QSize

from NeuroRuler.utils.constants import View, ThresholdFilter
import NeuroRuler.utils.constants as constants

# Note, do not use imports like
# from NeuroRuler.utils.global_vars import IMAGE_DICT
# This would make the global variables not work
import NeuroRuler.utils.global_vars as global_vars
import NeuroRuler.utils.imgproc as imgproc
import NeuroRuler.utils.user_settings as user_settings

def calculate_circumference(path) -> float:
    # set up ui
    app = QApplication(sys.argv)
    window = MainWindow()

    # load in image
    window.browse_files(False, path)
    window.set_view_z()
    window.orient_curr_image()
    window.disable_setting()
    user_settings.CONTOUR_COLOR = "red"
    binary_contour_slice: np.ndarray = window.render_curr_slice()
    return window.render_circumference(binary_contour_slice)

def labeled_result(path) -> float:
    with open(path, 'r') as file:
        line = file.readline().strip()
        parts = line.split('\t')
        last_section = parts[-1]
        return float(last_section)



def test_algorithm():
    labeled_data = []
    calculated_data = []
    data_folder = 'data'

    length = 0

    for file_name in os.listdir(data_folder):
        if file_name.endswith('.nrrd'):
            nrrd_prefix = os.path.splitext(file_name)[0][:10] # remove the file extension to get the prefix
            for tsv_file_name in os.listdir(data_folder):
                if nrrd_prefix in tsv_file_name and tsv_file_name.endswith('.tsv'):
                    length = length + 1
                    labeled_data.append(labeled_result(data_folder + "/" + tsv_file_name))
                    calculated_data.append(calculate_circumference(data_folder + "/" + file_name))
                    break
            else:
                continue

    r_square = np.corrcoef(labeled_data, calculated_data)[0, 1]
    assert length > 20
    assert r_square ** 2 > 0.98
"""GUI helper functions."""

import platform
import string
from typing import Union

import SimpleITK as sitk
import numpy as np

from PyQt6.QtGui import QImage, QColor, QPixmap, QIcon, QFont
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QLabel,
    QMainWindow,
    QFileDialog,
    QMenu,
    QVBoxLayout,
    QWidget,
    QMessageBox,
)
from PyQt6.QtCore import QSize
from PyQt6.QtCore import Qt

import qimage2ndarray

import NeuroRuler.utils.exceptions as exceptions
import NeuroRuler.utils.gui_settings as user_settings
from NeuroRuler.utils.constants import deprecated

MACOS: bool = "macOS" in platform.platform()
WINDOW_TITLE_PADDING: int = 12
"""Used in InformationDialog to add width to the dialog to prevent the window title from being truncated."""


# tl;dr QColor can have alpha (e.g., if we wanted contour color to be transparent)
# but we don't have a need for it so don't support it.
# Call hasAlphaChannel() on many of the QImage's we're working with results in False.
# qimage2ndarray supports scalar/gray + alpha and RGB + alpha, but perhaps the numpy arrays
# we get from sitk.Image don't have alpha. We don't need to go to the effort of adding alpha.
def string_to_QColor(name_or_hex: str) -> QColor:
    """Convert a name (e.g. red) or 6-hexit rrggbb string to a ``QColor``.

    :param name_or_hex: name of color (e.g. blue) or rrggbb (hexits)
    :type name_or_hex: str
    :return: QColor
    :rtype: QColor
    :raise: exceptions.InvalidColor if ``name_or_hex`` not in specified formats"""
    if name_or_hex.isalpha():
        return QColor(name_or_hex)
    if not all(char in string.hexdigits for char in name_or_hex):
        raise exceptions.InvalidColor(name_or_hex)

    channels: bytes = bytes.fromhex(name_or_hex)
    if len(channels) == 3:
        return QColor(channels[0], channels[1], channels[2])
    else:
        raise exceptions.InvalidColor(name_or_hex)


def mask_QImage(q_img: QImage, binary_mask: np.ndarray, color: QColor) -> None:
    """Given 2D ``q_img`` and 2D ``binary_mask`` of the same shape, apply ``binary_mask`` on ``q_img``
    to change ``q_img`` pixels corresponding to ``binary_mask``=1 to ``color``. Mutates ``q_img``.

    QImage and numpy use [reversed w,h order](https://stackoverflow.com/a/68220805/18479243).

    This function checks that
    ``q_img.size().width() == binary_mask.shape[0]`` and ``q_img.size().height() == binary_mask.shape[1]``.

    :param q_img:
    :type q_img: QImage
    :param binary_mask: 0|1 elements
    :type binary_mask: np.ndarray
    :param color:
    :type color: QColor
    :raise: exceptions.ArraysDifferentShape if the arrays are of different shape
    :return: None
    :rtype: None"""
    if (
        q_img.size().width() != binary_mask.shape[0]
        or q_img.size().height() != binary_mask.shape[1]
    ):
        raise exceptions.ArraysDifferentShape
    for i in range(binary_mask.shape[0]):
        for j in range(binary_mask.shape[1]):
            if binary_mask[i][j]:
                q_img.setPixelColor(i, j, color)


def sitk_slice_to_qimage(sitk_slice: sitk.Image) -> QImage:
    """Convert a 2D sitk.Image slice to a QImage.

    This function calls sitk.GetArrayFromImage, which returns the transpose.
    It also calls qimage2ndarray.array2qimage with normalize=True, normalizing
    the pixels to 0..255.

    :param sitk_slice: 2D slice
    :type sitk_slice: sitk.Image
    :return: 0..255 normalized QImage
    :rtype: QImage"""
    slice_np: np.ndarray = sitk.GetArrayFromImage(sitk_slice)
    return qimage2ndarray.array2qimage(slice_np, normalize=True)


class ErrorMessageBox(QMessageBox):
    def __init__(self, message: str):
        """:param message: Error message
        :type message: str"""
        super().__init__()
        # Window title is ignored on macOS.
        # QDialog's window title is not ignored on macOS, but I'm pretty sure QDialog doesn't
        # support icons.
        self.setWindowTitle("Error")
        self.setIconPixmap(
            QPixmap(f":/{user_settings.THEME_NAME}/message_critical.svg")
        )
        self.setText(message)


# adjustSize adjusts size based on window content, not window title (+ window buttons)
# So for some menu options, the window title would be truncated if some width isn't added
# However, QDialog does show window title on macOS (unlike QMessageBox)
class InformationDialog(QDialog):
    def __init__(self, title: str, message: str):
        """:param title: Title of window
        :type title: str
        :param message: Informational message
        :type message: str"""
        super().__init__()
        self.setWindowTitle(title)
        layout: QVBoxLayout = QVBoxLayout()
        message_label: QLabel = QLabel(message)
        layout.addWidget(message_label)
        self.setLayout(layout)
        self.adjustSize()
        # Add width to prevent truncation of the window title
        self.setFixedSize(
            self.size().width() + WINDOW_TITLE_PADDING * len(title),
            self.size().height(),
        )


# Deprecated because QMessageBox's window title doesn't show up on macOS
# However, QMessageBox can display an icon, whereas QDialog can't (I think)
# The icon provides some additional width that ill cause the window title to not be truncated, unlike QDialog
@deprecated
class InformationMessageBox(QMessageBox):
    def __init__(self, title: str, message: str):
        """:param title: Title of window (on macOS, QMessageBox window title doesn't show up so is instead prepended to the message)
        :type title: str
        :param message: Informational message
        :type message: str"""
        super().__init__()
        self.setWindowTitle(title)
        self.setIconPixmap(
            QPixmap(f":/{user_settings.THEME_NAME}/message_information.svg")
        )
        if MACOS:
            title += "\n\n"
        self.setText(f"{title if MACOS else ''} {message}")

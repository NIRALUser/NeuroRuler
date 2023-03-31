"""GUI helper functions.

Note, importing PyQt6 in any file that's imported by a test file will cause an error."""

import string
from typing import Union

import numpy as np
from PySide6.QtGui import QImage, QColor

import src.utils.exceptions as exceptions
import src.utils.user_settings as settings


def string_to_QColor(name_or_hex: str) -> QColor:
    """Convert a name (e.g. red) or 6-hexit rrggbb or 8-hexit rrggbbaa string to a `QColor`.

    :param name_or_hex: name of color or rrggbb or rrggbbaa
    :type name_or_hex: str
    :return: QColor
    :rtype: QColor
    :raise: exceptions.InvalidColor if `name_or_hex` not in specified formats"""
    if name_or_hex.isalpha():
        return QColor(name_or_hex)
    if not all(char in string.hexdigits for char in name_or_hex):
        raise exceptions.InvalidColor(name_or_hex)

    channels: bytes = bytes.fromhex(name_or_hex)
    if len(channels) == 3:
        return QColor(channels[0], channels[1], channels[2])
    elif len(channels) == 4:
        color = QColor(channels[0], channels[1], channels[2], alpha=channels[3])
        if settings.DEBUG:
            print(f"string_to_QColor received 8-hexit str, alpha = {color.alpha()}")
        return color
    else:
        raise exceptions.InvalidColor(name_or_hex)


def mask_QImage(
    q_img: QImage, binary_mask: np.ndarray, color: QColor, mutate: bool = True
) -> Union[None, QImage]:
    """Given 2D `q_img` and 2D `binary_mask` of the same shape, apply `binary_mask` on `q_img`
    to change `q_img` pixels corresponding to `binary_mask`=1 to `color`.

    QImage and numpy use [reversed w,h order](https://stackoverflow.com/a/68220805/18479243).

    This function checks that
    `q_img.size().width() == binary_mask.shape[0]` and `q_img.size().height() == binary_mask.shape[1]`.

    :param q_img:
    :type q_img: QImage
    :param binary_mask: 0|1 elements
    :type binary_mask: np.ndarray
    :param color:
    :type color: QColor
    :param mutate: Whether to mutate `q_img` or operate on a clone
    :type mutate: bool
    :raise: exceptions.ArraysDifferentShape if the arrays are of different shape
    :return: None (if `mutate`) or cloned QImage (if not `mutate`)
    :rtype: None or QImage"""
    base: QImage = q_img if mutate else q_img.copy()
    if (
        base.size().width() != binary_mask.shape[0]
        or base.size().height() != binary_mask.shape[1]
    ):
        raise exceptions.ArraysDifferentShape
    for i in range(binary_mask.shape[0]):
        for j in range(binary_mask.shape[1]):
            if binary_mask[i][j]:
                base.setPixelColor(i, j, color)
    if not mutate:
        return base

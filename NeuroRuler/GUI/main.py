"""Defines ``MainWindow`` and ``main()``, the entrypoint of the GUI.

Loads ``NeuroRuler/GUI/mainwindow.ui``, made in QtDesigner.

Loads ``.qss`` stylesheets and ``resources.py`` (icons) files, generated
by BreezeStyleSheets. Our fork of the repo: https://github.com/NIRALUser/BreezeStyleSheets.

If adding a new GUI element (in the GUI or in the menubar, whatever), you'll have to modify
modify __init__ and settings_view_toggle.

Edge cases: If this element should be disabled after enable_elements or enabled after disable_elements,
then you will need to modify those."""


import importlib
import sys
import os
import json
import re
import webbrowser
from pathlib import Path
from typing import Union

import SimpleITK as sitk
import numpy as np
from typing import Any

from PyQt6 import QtGui, QtCore
from PyQt6.QtGui import QPixmap, QAction, QImage, QIcon, QResizeEvent
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
from PyQt6.uic.load_ui import loadUi
from PyQt6.QtCore import Qt, QSize

import pprint
import pkg_resources
from NeuroRuler.utils.constants import View, ThresholdFilter
import NeuroRuler.utils.constants as constants

# Note, do not use imports like
# from NeuroRuler.utils.global_vars import IMAGE_DICT
# This would make the global variables not work
import NeuroRuler.utils.global_vars as global_vars
import NeuroRuler.utils.imgproc as imgproc
import NeuroRuler.utils.gui_settings as settings
from NeuroRuler.GUI.helpers import (
    string_to_QColor,
    mask_QImage,
    sitk_slice_to_qimage,
    ErrorMessageBox,
    InformationDialog,
)

from NeuroRuler.utils.img_helpers import (
    initialize_globals,
    update_images,
    get_curr_image,
    get_curr_image_size,
    get_curr_rotated_slice,
    get_curr_smooth_slice,
    get_curr_metadata,
    get_curr_binary_thresholded_slice,
    get_curr_otsu_slice,
    get_curr_physical_units,
    get_curr_path,
    get_all_paths,
    get_curr_properties_tuple,
    get_middle_dimension,
)

import NeuroRuler.utils.img_helpers as img_helpers


PATH_TO_UI_FILE: Path = Path("NeuroRuler") / "GUI" / "mainwindow.ui"
if not PATH_TO_UI_FILE.exists():
    PATH_TO_UI_FILE = Path(
        pkg_resources.resource_filename("NeuroRuler.GUI", "mainwindow.ui")
    )
PATH_TO_NR_LOGO: Path = Path("NeuroRuler") / "GUI" / "static" / "nr_logo.png"
if not PATH_TO_NR_LOGO.exists():
    PATH_TO_NR_LOGO = Path(
        pkg_resources.resource_filename("NeuroRuler.GUI", "static/nr_logo.png")
    )

SETTINGS_VIEW_ENABLED: bool = True
"""Whether the user is able to adjust settings (settings screen) or not
(circumference and contoured image screen)."""

DEFAULT_CIRCUMFERENCE_LABEL_TEXT: str = "Calculated Circumference: N/A"
DEFAULT_IMAGE_PATH_LABEL_TEXT: str = "Image path"
GITHUB_LINK: str = "https://github.com/NIRALUser/NeuroRuler"
DOCUMENTATION_LINK: str = "https://NeuroRuler.readthedocs.io/en/latest/"
DEFAULT_IMAGE_TEXT: str = "Select images using File > Open!"
DEFAULT_IMAGE_NUM_LABEL_TEXT: str = "Image 0 of 0"
DEFAULT_IMAGE_STATUS_TEXT: str = "Image path is displayed here."

UNSCALED_QPIXMAP: QPixmap
"""Unscaled QPixmap from which the scaled version is rendered in the GUI.

When any slice (rotated, smoothed, previewed) is rendered from an unscaled QImage, this variable is set to the
QPixmap generated from that unscaled QImage.

This variable will not change on resizeEvent. resizeEvent will scale this. Otherwise, if scaling
self.image's pixmap (which is already scaled), there would be loss of detail."""
OUTPUT_SLICE_EXTENSION: str = "png"


class MainWindow(QMainWindow):
    """Main window of the application.

    Settings mode and circumference mode."""

    def __init__(self):
        """Load main file and connect GUI events to methods/functions.

        Sets window title and icon."""
        super(MainWindow, self).__init__()
        loadUi(str(PATH_TO_UI_FILE), self)

        self.setWindowTitle("NeuroRuler")

        self.action_open.triggered.connect(lambda: self.browse_files(False))
        self.action_add_images.triggered.connect(lambda: self.browse_files(True))
        self.action_remove_image.triggered.connect(self.remove_curr_img)
        self.action_exit.triggered.connect(exit)
        self.action_github.triggered.connect(lambda: webbrowser.open(GITHUB_LINK))
        self.action_documentation.triggered.connect(
            lambda: webbrowser.open(DOCUMENTATION_LINK)
        )
        self.action_show_credits.triggered.connect(
            lambda: information_dialog(
                "Credits",
                'Credit to Jesse Wei, Madison Lester, Peifeng "Hank" He, Eric Schneider, and Martin Styner.\n\nUniversity of North Carolina at Chapel Hill, 2023. See the GitHub page for more info.',
            )
        )
        self.action_show_dimensions.triggered.connect(display_dimensions)
        self.action_show_properties.triggered.connect(display_properties)
        self.action_show_direction.triggered.connect(display_direction)
        self.action_show_spacing.triggered.connect(display_spacing)
        self.action_export_json.triggered.connect(self.export_json)
        self.action_export_png.triggered.connect(
            lambda: self.export_curr_slice_as_img("png")
        )
        self.action_export_jpg.triggered.connect(
            lambda: self.export_curr_slice_as_img("jpg")
        )
        self.action_export_bmp.triggered.connect(
            lambda: self.export_curr_slice_as_img("bmp")
        )
        self.action_export_ppm.triggered.connect(
            lambda: self.export_curr_slice_as_img("ppm")
        )
        self.action_export_xbm.triggered.connect(
            lambda: self.export_curr_slice_as_img("xbm")
        )
        self.action_export_xpm.triggered.connect(
            lambda: self.export_curr_slice_as_img("xpm")
        )
        self.action_import_image_settings.triggered.connect(self.import_json)
        self.next_button.clicked.connect(self.next_img)
        self.previous_button.clicked.connect(self.previous_img)
        self.apply_button.clicked.connect(self.settings_export_view_toggle)
        self.x_slider.valueChanged.connect(self.rotate_x)
        self.y_slider.valueChanged.connect(self.rotate_y)
        self.z_slider.valueChanged.connect(self.rotate_z)
        self.slice_slider.valueChanged.connect(self.slice_update)
        self.reset_button.clicked.connect(self.reset_settings)
        self.smoothing_preview_button.clicked.connect(self.render_smooth_slice)
        self.otsu_radio_button.clicked.connect(self.disable_binary_threshold_inputs)
        self.binary_radio_button.clicked.connect(self.enable_binary_threshold_inputs)
        self.threshold_preview_button.clicked.connect(self.render_threshold)
        self.x_view_radio_button.clicked.connect(self.update_view)
        self.y_view_radio_button.clicked.connect(self.update_view)
        self.z_view_radio_button.clicked.connect(self.update_view)

        self.export_button.clicked.connect(self.export_json)

    def enable_elements(self) -> None:
        """Called after File > Open.

        Enables GUI elements. Explicitly disables some (e.g., Export CSV menu item and
        binary threshold inputs, since Otsu is default).

        :return: None
        """
        # findChildren searches recursively by default
        for widget in self.findChildren(QWidget):
            widget.setEnabled(True)

        # Menu stuff
        for widget in self.findChildren(QAction):
            widget.setEnabled(True)

        self.action_export_json.setEnabled(not SETTINGS_VIEW_ENABLED)
        self.export_button.setEnabled(not SETTINGS_VIEW_ENABLED)
        self.disable_binary_threshold_inputs()

    def enable_binary_threshold_inputs(self) -> None:
        """Called when Binary filter button is clicked.

        Restore binary input box.

        :return: None
        """
        self.upper_threshold_input.setEnabled(True)
        self.lower_threshold_input.setEnabled(True)

    def settings_export_view_toggle(self) -> None:
        """Called when clicking Apply (in settings mode) or Adjust (in circumference mode).

        Toggle SETTINGS_VIEW_ENABLED, change apply button text, render stuff depending on the current mode.

        Enables/disables GUI elements depending on the value of SETTINGS_VIEW_ENABLED.

        :return: None
        """
        # Unsure sure why this is necessary here but nowhere else...
        global SETTINGS_VIEW_ENABLED
        SETTINGS_VIEW_ENABLED = not SETTINGS_VIEW_ENABLED
        settings_view_enabled = SETTINGS_VIEW_ENABLED
        if settings_view_enabled:
            self.apply_button.setText("Apply")
            self.circumference_label.setText(DEFAULT_CIRCUMFERENCE_LABEL_TEXT)
            # Render uncontoured slice after pressing adjust
            self.render_curr_slice()
        else:
            self.apply_button.setText("Adjust")

            # When clicking Apply, the circumference should be calculated only for the axial slice.
            # Edge case: If the user does a huge rotation, then switching to axial view may not display an
            # axial slice. For example, after clicking coronal and setting X rotation to 90,
            # clicking axial will not show an axial slice.
            # We could just not change the view and re-orient when clicking Apply if this is a valid use case (probably isn't).
            # TODO: Check with Styner
            self.set_view_z()
            self.orient_curr_image()

            self.update_smoothing_settings(True)
            self.update_binary_filter_settings(True)
            # Ignore the type annotation warning here.
            # render_curr_slice() must return np.ndarray since not settings_view_enabled here
            binary_contour_slice: np.ndarray = self.render_curr_slice()
            self.render_circumference(binary_contour_slice)

        # Open button is always enabled.
        # If pressing it in circumference mode, then browse_files() will toggle to settings view.
        self.action_open.setEnabled(True)
        self.action_import_image_settings.setEnabled(settings_view_enabled)
        self.action_add_images.setEnabled(settings_view_enabled)
        self.action_remove_image.setEnabled(settings_view_enabled)
        self.x_slider.setEnabled(settings_view_enabled)
        self.y_slider.setEnabled(settings_view_enabled)
        self.z_slider.setEnabled(settings_view_enabled)
        self.slice_slider.setEnabled(settings_view_enabled)
        self.x_rotation_label.setEnabled(settings_view_enabled)
        self.y_rotation_label.setEnabled(settings_view_enabled)
        self.z_rotation_label.setEnabled(settings_view_enabled)
        self.slice_num_label.setEnabled(settings_view_enabled)
        self.reset_button.setEnabled(settings_view_enabled)
        self.smoothing_preview_button.setEnabled(settings_view_enabled)
        self.otsu_radio_button.setEnabled(settings_view_enabled)
        self.binary_radio_button.setEnabled(settings_view_enabled)
        self.lower_threshold.setEnabled(settings_view_enabled)
        self.lower_threshold_input.setEnabled(settings_view_enabled)
        self.upper_threshold.setEnabled(settings_view_enabled)
        self.upper_threshold_input.setEnabled(settings_view_enabled)
        self.threshold_preview_button.setEnabled(settings_view_enabled)
        self.action_export_json.setEnabled(not settings_view_enabled)
        self.circumference_label.setEnabled(not settings_view_enabled)
        self.export_button.setEnabled(not settings_view_enabled)
        self.smoothing_preview_button.setEnabled(settings_view_enabled)
        self.conductance_parameter_label.setEnabled(settings_view_enabled)
        self.conductance_parameter_input.setEnabled(settings_view_enabled)
        self.smoothing_iterations_label.setEnabled(settings_view_enabled)
        self.smoothing_iterations_input.setEnabled(settings_view_enabled)
        self.time_step_label.setEnabled(settings_view_enabled)
        self.time_step_input.setEnabled(settings_view_enabled)
        self.x_view_radio_button.setEnabled(settings_view_enabled)
        self.y_view_radio_button.setEnabled(settings_view_enabled)
        self.z_view_radio_button.setEnabled(settings_view_enabled)
        self.lower_threshold_input.setEnabled(
            settings_view_enabled and self.binary_radio_button.isChecked()
        )
        self.upper_threshold_input.setEnabled(
            settings_view_enabled and self.binary_radio_button.isChecked()
        )

    def disable_binary_threshold_inputs(self) -> None:
        """Called when Otsu filter button is clicked.

        Disable binary threshold input boxes.

        :return: None
        """
        self.upper_threshold_input.setEnabled(False)
        self.lower_threshold_input.setEnabled(False)

    def disable_elements(self) -> None:
        """Called when the list is now empty, i.e. just removed from list of length 1.

        Explicitly enables elements that should never be disabled and sets default text.

        :return: None
        """
        central_widget = self.findChildren(QWidget, "centralwidget")[0]
        menubar = self.menuBar()

        for gui_element in central_widget.findChildren(QWidget):
            gui_element.setEnabled(False)

        # findChildren searches recursively by default
        for menu in menubar.findChildren(QMenu):
            for action in menu.actions():
                action.setEnabled(False)

        self.action_open.setEnabled(True)
        self.circumference_label.setText(DEFAULT_CIRCUMFERENCE_LABEL_TEXT)
        self.image.setEnabled(True)
        self.image.clear()
        self.image.setText(DEFAULT_IMAGE_TEXT)
        self.image.setStatusTip(DEFAULT_IMAGE_STATUS_TEXT)
        self.image_path_label.setText(DEFAULT_IMAGE_PATH_LABEL_TEXT)
        self.image_num_label.setText(DEFAULT_IMAGE_NUM_LABEL_TEXT)
        self.apply_button.setText("Apply")
        self.z_view_radio_button.setChecked(True)

    def browse_files(self, extend: bool, path=None) -> None:
        """Called after File > Open or File > Add Images.

        If ``extend``, then ``IMAGE_DICT`` will be updated with new images.

        Else, ``IMAGE_DICT`` will be cleared and
        (re)initialized (e.g. when choosing files for the first time or re-opening).

        Opens file menu.

        Renders various elements depending on the value of ``extend``.

        If called in circumference mode, then will toggle to settings mode.

        :param extend: Whether to clear IMAGE_DICT and (re)initialize or add images to it. Determines which GUI elements are rendered.
        :param path: Used for unit testing, when only one path is imported. Normally, the path(s) are selected by user in a QFileDialog.
        :type extend: bool
        :return: None"""
        # If called in circumference mode, then toggle to settings mode.
        if not SETTINGS_VIEW_ENABLED:
            self.settings_export_view_toggle()

        if path is None:
            file_filter: str = "MRI images " + str(
                constants.SUPPORTED_IMAGE_EXTENSIONS
            ).replace("'", "").replace(",", "")

            files = QFileDialog.getOpenFileNames(
                self,
                "Open files",
                str(settings.FILE_BROWSER_START_DIR),
                file_filter,
            )
            # list[str]
            path_list = files[0]
            if len(path_list) == 0:
                return
        else:
            path_list = [path]

        # Convert to list[Path]. Slight inefficiency but worth.
        path_list = list(map(Path, path_list))

        differing_images: list[Path]

        if not extend:
            differing_images = initialize_globals(path_list)
            # Set view to z because initialize_globals calls update_images, which orients loaded images
            # for the axial view
            self.set_view_z()
            self.render_all_sliders()
            self.enable_elements()
            self.render_curr_slice()
            if differing_images:
                newline: str = "\n"
                error_message_box(
                    f"The image(s) you uploaded have differing properties.\n"
                    f"The first one and all images with properties matching the first one have been loaded.\n"
                    f"The name(s) of the ones with differing properties are\n\n"
                    f"{newline.join([path.name for path in differing_images])}"
                )
        else:
            # Doesn't need to re-render sliders to set max value of slice slider.
            # update_images won't change max value of slice slicer.
            # Does not need to render current slice. Images are added to the end of the dict.
            # And adding duplicate key doesn't change key order.
            differing_images = update_images(path_list)
            if differing_images:
                newline: str = "\n"
                error_message_box(
                    f"You have uploaded image(s) with properties that differ from those of the currently loaded ones.\n"
                    f"These image(s) have not been loaded:\n\n"
                    f"{newline.join([path.name for path in differing_images])}"
                )
        # When extending, image num must be updated
        self.render_image_num_and_path()

    def update_view(self) -> None:
        """Called when clicking on any of the three view radio buttons.

        Sets global_vars.VIEW to the correct value. Then orients the current image and renders.

        :return: None
        """
        # The three buttons are in a button group in the  file
        # And all have autoExclusive=True
        if self.x_view_radio_button.isChecked():
            global_vars.VIEW = constants.View.X
        elif self.y_view_radio_button.isChecked():
            global_vars.VIEW = constants.View.Y
        else:
            global_vars.VIEW = constants.View.Z

        self.orient_curr_image()
        self.render_curr_slice()

    def set_view_z(self) -> None:
        """Set global_vars.VIEW to View.Z and set the z radio button to checked.

        :return: None
        """
        global_vars.VIEW = constants.View.Z
        # TODO: Uncheck x and y are technically unnecessary since these 3 buttons in the view_button_group have
        # autoExclusive=True
        self.x_view_radio_button.setChecked(False)
        self.y_view_radio_button.setChecked(False)
        self.z_view_radio_button.setChecked(True)

    def update_smoothing_settings(self, set_global_vars_to_GUI_text: bool) -> None:
        """Update smoothing text in the GUI and set SMOOTHING_FILTER parameters.

        :param set_global_vars_to_GUI_text: If True, will first try to modify global_vars variables to the text in the GUI before updating GUI text and filter parameters. If False, will not do so.
        :type set_global_vars_to_GUI_text: bool
        :return: None
        """
        if set_global_vars_to_GUI_text:
            try:
                global_vars.CONDUCTANCE_PARAMETER = float(
                    self.conductance_parameter_input.displayText()
                )
            except ValueError:
                if settings.DEBUG:
                    print("Conductance must be a float!")
        self.conductance_parameter_input.setText(str(global_vars.CONDUCTANCE_PARAMETER))
        self.conductance_parameter_input.setPlaceholderText(
            str(global_vars.CONDUCTANCE_PARAMETER)
        )
        global_vars.SMOOTHING_FILTER.SetConductanceParameter(
            global_vars.CONDUCTANCE_PARAMETER
        )

        if set_global_vars_to_GUI_text:
            try:
                global_vars.SMOOTHING_ITERATIONS = int(
                    self.smoothing_iterations_input.displayText()
                )
            except ValueError:
                if settings.DEBUG:
                    print("Iterations must be an integer!")
        self.smoothing_iterations_input.setText(str(global_vars.SMOOTHING_ITERATIONS))
        self.smoothing_iterations_input.setPlaceholderText(
            str(global_vars.SMOOTHING_ITERATIONS)
        )
        global_vars.SMOOTHING_FILTER.SetNumberOfIterations(
            global_vars.SMOOTHING_ITERATIONS
        )

        if set_global_vars_to_GUI_text:
            try:
                global_vars.TIME_STEP = float(self.time_step_input.displayText())
            except ValueError:
                if settings.DEBUG:
                    print("Time step must be a float!")
        self.time_step_input.setText(str(global_vars.TIME_STEP))
        self.time_step_input.setPlaceholderText(str(global_vars.TIME_STEP))
        global_vars.SMOOTHING_FILTER.SetTimeStep(global_vars.TIME_STEP)

    def update_binary_filter_settings(self, set_global_vars_to_GUI_text: bool) -> None:
        """Updates binary threshold filter text in the GUI and set BINARY_THRESHOLD_FILTER parameters.

        :param set_global_vars_to_GUI_text: If True, will first try to modify global_vars variables to the text in the GUI before updating GUI text and filter parameters. If False, will not do so.
        :type set_global_vars_to_GUI_text: bool
        :return: None
        """
        if set_global_vars_to_GUI_text:
            try:
                global_vars.LOWER_BINARY_THRESHOLD = float(
                    self.lower_threshold_input.displayText()
                )
            except ValueError:
                pass
        self.lower_threshold_input.setText(str(global_vars.LOWER_BINARY_THRESHOLD))
        self.lower_threshold_input.setPlaceholderText(
            str(global_vars.LOWER_BINARY_THRESHOLD)
        )
        global_vars.BINARY_THRESHOLD_FILTER.SetLowerThreshold(
            global_vars.LOWER_BINARY_THRESHOLD
        )

        if set_global_vars_to_GUI_text:
            try:
                global_vars.UPPER_BINARY_THRESHOLD = float(
                    self.upper_threshold_input.displayText()
                )
            except ValueError:
                pass
        self.upper_threshold_input.setText(str(global_vars.UPPER_BINARY_THRESHOLD))
        self.upper_threshold_input.setPlaceholderText(
            str(global_vars.UPPER_BINARY_THRESHOLD)
        )
        global_vars.BINARY_THRESHOLD_FILTER.SetUpperThreshold(
            global_vars.UPPER_BINARY_THRESHOLD
        )

    def render_scaled_qpixmap_from_qimage(self, q_img: QImage) -> None:
        """Convert q_img to QPixmap and set self.image's pixmap to that pixmap scaled to self.image's size.

        Sets UNSCALED_PIXMAP to the unscaled pixmap generated from the q_img.

        :param q_img:
        :type q_img: QImage
        :return: None"""
        global UNSCALED_QPIXMAP
        UNSCALED_QPIXMAP = QPixmap(q_img)
        self.image.setPixmap(
            UNSCALED_QPIXMAP.scaled(
                self.image.size(),
                aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                transformMode=Qt.TransformationMode.SmoothTransformation,
            )
        )

    def resizeEvent(self, event: QResizeEvent) -> None:
        """This method is called every time the window is resized. Overrides PyQt6's resizeEvent.

        Sets pixmap to UNSCALED_QPIXMAP scaled to self.image's size.

        :param event:
        :type event: QResizeEvent
        :return: None"""
        if global_vars.IMAGE_DICT:
            self.image.setPixmap(
                UNSCALED_QPIXMAP.scaled(
                    self.image.size(),
                    aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                    transformMode=Qt.TransformationMode.SmoothTransformation,
                )
            )
        QMainWindow.resizeEvent(self, event)

    def render_curr_slice(self) -> Union[np.ndarray, None]:
        """Resamples the currently selected image using its rotation and slice settings,
        then renders the resulting slice (scaled to the size of self.image) in the GUI.

        DOES NOT set text for ``image_num_label`` and file path labels.

        If ``not SETTINGS_VIEW_ENABLED``, also calls ``imgproc.contour()`` and outlines
        the contour of the QImage (mutating it).

        Additionally, also returns a view of the binary contoured slice if ``not SETTINGS_VIEW_ENABLED``.
        This saves work when computing circumference.

        :return: np.ndarray if ``not SETTINGS_VIEW_ENABLED`` else None
        :rtype: np.ndarray or None"""

        if not SETTINGS_VIEW_ENABLED:
            self.set_view_z()

        rotated_slice: sitk.Image = get_curr_rotated_slice()
        q_img: QImage = sitk_slice_to_qimage(rotated_slice)
        rv_dummy_var: np.ndarray = np.zeros(0)

        if not SETTINGS_VIEW_ENABLED:
            if self.otsu_radio_button.isChecked():
                binary_contour_slice: np.ndarray = imgproc.contour(
                    rotated_slice, ThresholdFilter.Otsu
                )
            else:
                binary_contour_slice: np.ndarray = imgproc.contour(
                    rotated_slice, ThresholdFilter.Binary
                )
            rv_dummy_var = binary_contour_slice
            mask_QImage(
                q_img,
                np.transpose(binary_contour_slice),
                string_to_QColor(settings.CONTOUR_COLOR),
            )

        elif global_vars.VIEW != constants.View.Z:
            z_indicator: np.ndarray = np.zeros(
                (rotated_slice.GetSize()[1], rotated_slice.GetSize()[0])
            )
            z_indicator[get_curr_image_size()[2] - global_vars.SLICE - 1, :] = 1
            mask_QImage(
                q_img,
                np.transpose(z_indicator),
                string_to_QColor(settings.CONTOUR_COLOR),
            )

        self.render_scaled_qpixmap_from_qimage(q_img)

        if not SETTINGS_VIEW_ENABLED:
            return rv_dummy_var

    def render_smooth_slice(self) -> None:
        """Renders smooth slice in GUI. Allows user to preview result of smoothing settings.

        :return: None"""
        self.update_smoothing_settings(True)
        # Preview should apply filter only on axial slice
        self.set_view_z()
        smooth_slice: sitk.Image = get_curr_smooth_slice()
        q_img: QImage = sitk_slice_to_qimage(smooth_slice)
        self.render_scaled_qpixmap_from_qimage(q_img)

    def render_threshold(self) -> None:
        """Render filtered image slice on UI.

        :return: None"""
        # Preview should apply filter only on axial slice
        self.set_view_z()
        if self.otsu_radio_button.isChecked():
            filter_img: sitk.Image = get_curr_otsu_slice()
        else:
            self.update_binary_filter_settings(True)
            filter_img: sitk.Image = get_curr_binary_thresholded_slice()
        q_img: QImage = sitk_slice_to_qimage(filter_img)
        self.render_scaled_qpixmap_from_qimage(q_img)

    def render_circumference(self, binary_contour_slice: np.ndarray) -> float:
        """Called after pressing Apply or when
        (not SETTINGS_VIEW_ENABLED and (pressing Next or Previous or Remove Image))

        Computes circumference from binary_contour_slice and renders circumference label.

        binary_contour_slice is always the return value of render_curr_slice since render_curr_slice must have
        already been called. If calling this function, render_curr_slice must have been called first.

        :param binary_contour_slice: Result of previously calling render_curr_slice when ``not SETTINGS_VIEW_ENABLED``
        :type binary_contour_slice: np.ndarray
        :return: circumference
        :rtype: float"""
        if SETTINGS_VIEW_ENABLED:
            raise Exception("Rendering circumference label when SETTINGS_VIEW_ENABLED")
        units: Union[str, None] = get_curr_physical_units()

        # Euler3D rotation has no effect on spacing (see unit test). This is the correct spacing
        # This is also the same as get_curr_rotated_slice().GetSpacing(), just without index [2]
        spacing: tuple = get_curr_image().GetSpacing()

        if settings.DEBUG:
            print(f"Computing circumference, and this is the spacing: {spacing}")

        # TODO
        # binary_contour_slice is the transpose of the rotated_slice
        # Thus, should pass spacing values in the reverse order?
        circumference: float = imgproc.length_of_contour_with_spacing(
            binary_contour_slice, spacing[0], spacing[1]
        )
        # circumference: float = imgproc.length_of_contour(binary_contour_slice)
        self.circumference_label.setText(
            f"Calculated Circumference: {round(circumference, constants.NUM_DIGITS_TO_ROUND_TO)} {units if units is not None else constants.MESSAGE_TO_SHOW_IF_UNITS_NOT_FOUND}"
        )
        return circumference

    def toggle_setting_to_false(self) -> None:
        """Used in testing.

        Flipping the SETTINGS_VIEW_ENABLED

        :return: None"""
        global SETTINGS_VIEW_ENABLED
        if SETTINGS_VIEW_ENABLED:
            SETTINGS_VIEW_ENABLED = not SETTINGS_VIEW_ENABLED

    def toggle_setting_to_true(self) -> None:
        """Used in testing.

        Flipping the SETTINGS_VIEW_ENABLED

        :return: None"""
        global SETTINGS_VIEW_ENABLED
        if not SETTINGS_VIEW_ENABLED:
            SETTINGS_VIEW_ENABLED = not SETTINGS_VIEW_ENABLED

    def render_image_num_and_path(self) -> None:
        """Set image_num_label, image_path_label, and status tip of the image.

        Called when pressing Next or Previous (next_img, prev_img), and after File > Open (browse_files).

        Also called when removing an image.

        :return: None"""
        self.image_num_label.setText(
            f"Image {global_vars.CURR_IMAGE_INDEX + 1} of {len(global_vars.IMAGE_DICT)}"
        )
        self.image_path_label.setText(str(get_curr_path().name))
        self.image_path_label.setStatusTip(str(get_curr_path()))
        self.image.setStatusTip(str(get_curr_path()))

    def render_all_sliders(self) -> None:
        """Sets all slider values to the global rotation and slice values.
        Also updates maximum value of slice slider.

        Called on reset. Will need to be called when updating batch index, if we implement this.

        Not called when the user updates a slider.

        Also updates rotation and slice num labels.

        :return: None"""
        self.x_slider.setValue(global_vars.THETA_X)
        self.y_slider.setValue(global_vars.THETA_Y)
        self.z_slider.setValue(global_vars.THETA_Z)
        self.slice_slider.setMaximum(get_curr_image().GetSize()[View.Z.value] - 1)
        self.slice_slider.setValue(global_vars.SLICE)
        self.x_rotation_label.setText(f"X rotation: {global_vars.THETA_X}°")
        self.y_rotation_label.setText(f"Y rotation: {global_vars.THETA_Y}°")
        self.z_rotation_label.setText(f"Z rotation: {global_vars.THETA_Z}°")
        self.slice_num_label.setText(f"Slice: {global_vars.SLICE}")

    def rotate_x(self) -> None:
        """Called when the user updates the x slider.

        Render image and set ``x_rotation_label``.

        :return: None"""
        x_slider_val: int = self.x_slider.value()
        global_vars.THETA_X = x_slider_val
        self.render_curr_slice()
        self.x_rotation_label.setText(f"X rotation: {x_slider_val}°")

    def rotate_y(self) -> None:
        """Called when the user updates the y slider.

        Render image and set ``y_rotation_label``.

        :return: None"""
        y_slider_val: int = self.y_slider.value()
        global_vars.THETA_Y = y_slider_val
        self.render_curr_slice()
        self.y_rotation_label.setText(f"Y rotation: {y_slider_val}°")

    def rotate_z(self) -> None:
        """Called when the user updates the z slider.

        Render image and set ``z_rotation_label``.

        :return: None"""
        z_slider_val: int = self.z_slider.value()
        global_vars.THETA_Z = z_slider_val
        self.render_curr_slice()
        self.z_rotation_label.setText(f"Z rotation: {z_slider_val}°")

    def slice_update(self) -> None:
        """Called when the user updates the slice slider.

        Render image and set ``slice_num_label``.

        :return: None"""
        slice_slider_val: int = self.slice_slider.value()
        global_vars.SLICE = slice_slider_val
        self.render_curr_slice()
        self.slice_num_label.setText(f"Slice: {slice_slider_val}")

    def reset_settings(self) -> None:
        """Called when Reset is clicked.

        Resets rotation values to 0 and slice num to the default ``int((z-1)/2)``
        for the current image, then renders current image and sliders.

        :return: None"""
        global_vars.THETA_X = 0
        global_vars.THETA_Y = 0
        global_vars.THETA_Z = 0
        global_vars.SLICE = get_middle_dimension(get_curr_image(), View.Z)
        self.render_curr_slice()
        self.render_all_sliders()

    def next_img(self) -> None:
        """Called when Next button is clicked.

        Advance index and render.

        :return: None"""
        img_helpers.next_img()
        # TODO: This feels inefficient...
        self.orient_curr_image()
        binary_contour_or_none: Union[np.ndarray, None] = self.render_curr_slice()
        self.render_image_num_and_path()

        if not SETTINGS_VIEW_ENABLED:
            # Ignore the type annotation warning. binary_contour_or_none must be binary_contour since not SETTINGS_VIEW_ENABLED
            self.render_circumference(binary_contour_or_none)

    def previous_img(self) -> None:
        """Called when Previous button is clicked.

        Decrement index and render.

        :return: None"""
        img_helpers.previous_img()
        # TODO: This feels inefficient...
        self.orient_curr_image()
        binary_contour_or_none: Union[np.ndarray, None] = self.render_curr_slice()
        self.render_image_num_and_path()

        if not SETTINGS_VIEW_ENABLED:
            # Ignore the type annotation warning. binary_contour_or_none must be binary_contour since not SETTINGS_VIEW_ENABLED
            self.render_circumference(binary_contour_or_none)

    # TODO: Due to the images now being a dict, we can
    # easily let the user remove a range of images if they want
    def remove_curr_img(self) -> None:
        """Called after File > Remove File.

        Removes current image from ``IMAGE_DICT``. Since ``IMAGE_DICT`` is a reference to an image dict
        in ``IMAGE_GROUPS``, it's removed from ``IMAGE_GROUPS`` as well.

        :return: None"""
        img_helpers.del_curr_img()

        if len(global_vars.IMAGE_DICT) == 0:
            self.disable_elements()
            return

        binary_contour_or_none: Union[np.ndarray, None] = self.render_curr_slice()
        self.render_image_num_and_path()

        if not SETTINGS_VIEW_ENABLED:
            # Ignore the type annotation warning. binary_contour_or_none must be binary_contour since not SETTINGS_VIEW_ENABLED
            self.render_circumference(binary_contour_or_none)

    def test_stuff(self) -> None:
        """Connected to Debug > Test stuff. Dummy button and function for easily testing stuff.

        Assume that anything you put here will be overwritten freely.

        :return: None"""
        self.image.setPixmap(QPixmap(f":/{settings.THEME_NAME}/help.svg"))
        self.image.setStatusTip(
            "This is intentional, if it's a question mark then that's good :), means we can display icons"
        )

    # TODO: File name should also include circumference when not SETTINGS_VIEW_ENABLED?
    def export_curr_slice_as_img(self, extension: str) -> None:
        """Called when an Export as image menu item is clicked.

        Exports ``self.image`` to ``constants.OUTPUT_DIR/image_stem/``. Thus, calling this when ``SETTINGS_VIEW_ENABLED`` will
        save a non-contoured image. Calling this when ``not SETTINGS_VIEW_ENABLED`` will save a contoured
        image.

        Filename has format <file_name>[_contoured].<extension>

        _contoured will be in the name if ``not SETTINGS_VIEW_ENABLED``.

        Supported formats in this function are the ones supported by QPixmap,
        namely BMP, JPG, JPEG, PNG, PPM, XBM, XPM.

        :param extension: BMP, JPG, JPEG, PNG, PPM, XBM, XPM
        :type extension: str
        :param path:
        :type path: Path
        :return: ``None``"""
        file_stem: str = constants.get_path_stem(get_curr_path())
        output_path: Path = constants.OUTPUT_DIR / file_stem

        if not output_path.exists():
            output_path.mkdir()

        path: str = str(
            output_path
            / f"{file_stem}{'_contoured' if not SETTINGS_VIEW_ENABLED else ''}.{extension}"
        )
        self.image.pixmap().save(path, extension)

    def import_json(self) -> None:
        """Called when "import" button is clicked

        Imported parameters include input_image_path, output_contoured_slice_path, x_rotation, y_rotation, z_rotation, slice,
        smoothing_conductance, smoothing_iterations, smoothing_time_step, threshold_filter, upper_binary_threshold, lower_binary_threshold,
        and circumference

        input_image_path is the only mandatory field.

        :return: `None`"""
        file_filter: str = "NeuroRuler image settings JSON " + str(("*.json")).replace(
            "'", ""
        ).replace(",", "")

        files, _ = QFileDialog.getOpenFileNames(
            self, "Open file", str(settings.FILE_BROWSER_START_DIR), file_filter
        )

        # list[str]
        path_list = files
        if len(path_list) == 0:
            return
        elif "gui_config" in path_list[0]:
            information_dialog(
                "Invalid JSON",
                "You selected a GUI configuration file. Please select an image settings JSON (fields circumference, x_rotation, y_rotation, etc.).",
            )
            return
        elif len(path_list) > 1:
            information_dialog(
                "Multiple imports",
                "Multiple JSON files were selected. Only the first will be imported.",
            )

        with open(path_list[0], "r") as file:
            # Parse the JSON data into a dictionary
            data = json.load(file)

        image_path: str = data["input_image_path"]
        self.browse_files(False, image_path)

        if "x_rotation" in data:
            global_vars.THETA_X = data["x_rotation"]
            self.x_slider.setValue(global_vars.THETA_X)

        if "y_rotation" in data:
            global_vars.THETA_Y = data["y_rotation"]
            self.y_slider.setValue(global_vars.THETA_Y)

        if "z_rotation" in data:
            global_vars.THETA_Z = data["z_rotation"]
            self.z_slider.setValue(global_vars.THETA_Z)

        self.update_view()

        if "slice" in data:
            global_vars.SLICE = data["slice"]
            self.slice_slider.setValue(global_vars.SLICE)
            self.slice_update()

        if "smoothing_conductance" in data:
            global_vars.CONDUCTANCE_PARAMETER = data["smoothing_conductance"]

        if "smoothing_iterations" in data:
            global_vars.SMOOTHING_ITERATIONS = data["smoothing_iterations"]

        if "smoothing_time_step" in data:
            global_vars.TIME_STEP = data["smoothing_time_step"]

        self.update_smoothing_settings(False)

        if "threshold_filter" in data:
            if data["threshold_filter"] == "Binary":
                if (
                    not "upper_binary_threshold" in data
                    or not "lower_binary_threshold" in data
                ):
                    print(
                        "If the imported JSON has threshold_filter Binary, it must have upper_binary_threshold and lower_binary_threshold"
                    )
                    exit(1)
                global_vars.UPPER_BINARY_THRESHOLD = data["upper_binary_threshold"]
                global_vars.LOWER_BINARY_THRESHOLD = data["lower_binary_threshold"]
                self.update_binary_filter_settings(False)
                self.enable_binary_threshold_inputs()
                self.binary_radio_button.click()
            elif data["threshold_filter"] == "Otsu":
                self.otsu_radio_button.click()
                self.disable_binary_threshold_inputs()
            else:
                print("Invalid threshold_filter in imported JSON")
                exit(1)

    def export_json(self) -> None:
        """Called when "export" button is clicked and when Menu > Export > JSON is clicked.

        Exported parameters include: input_image_path, output_contoured_slice_path, x_rotation, y_rotation, z_rotation, slice,
        smoothing_conductance, smoothing_iterations, smoothing_time_step, threshold_filter, upper_binary_threshold, lower_binary_threshold,
        and circumference

        :return: `None`"""

        global_vars.CURR_IMAGE_INDEX = 0
        self.render_image_num_and_path()
        for image_num in range(len(global_vars.IMAGE_DICT)):
            curr_path: Path = get_curr_path()
            stem: str = constants.get_path_stem(curr_path)
            binary_contour_slice: np.ndarray = self.render_curr_slice()
            circumference: float = self.render_circumference(binary_contour_slice)
            output_dir: Path = constants.OUTPUT_DIR / stem
            if not output_dir.exists():
                output_dir.mkdir()

            self.export_curr_slice_as_img(OUTPUT_SLICE_EXTENSION)

            data: dict[str, Any] = {
                "input_image_path": str(curr_path),
                "output_contoured_slice_path": str(
                    Path.cwd()
                    / output_dir
                    / (stem + f"_contoured.{OUTPUT_SLICE_EXTENSION}")
                ),
                "circumference": circumference,
                "x_rotation": global_vars.THETA_X,
                "y_rotation": global_vars.THETA_Y,
                "z_rotation": global_vars.THETA_Z,
                "slice": global_vars.SLICE,
                "smoothing_conductance": global_vars.CONDUCTANCE_PARAMETER,
                "smoothing_iterations": global_vars.SMOOTHING_ITERATIONS,
                "smoothing_time_step": global_vars.TIME_STEP,
                "threshold_filter": "Otsu"
                if self.otsu_radio_button.isChecked()
                else "Binary",
                "upper_binary_threshold": global_vars.UPPER_BINARY_THRESHOLD,
                "lower_binary_threshold": global_vars.LOWER_BINARY_THRESHOLD,
            }
            # Otsu doesn't use the upper/lower binary thresholds set in the GUI
            if data["threshold_filter"] == "Otsu":
                data.pop("upper_binary_threshold")
                data.pop("lower_binary_threshold")

            with open(output_dir / (stem + "_settings.json"), "w") as outfile:
                json.dump(data, outfile, indent=4)

            self.next_img()

    def orient_curr_image(self) -> None:
        """Orient the current image for the current view (global_vars.VIEW) by applying ORIENT_FILTER on it.

        This mutates the image.

        :return: None"""
        img_helpers.orient_curr_image(global_vars.VIEW)


def error_message_box(message: str) -> None:
    """Creates a message box with an error message and red warning icon.

    :param message: the error message to be displayed
    :type message: str
    :return: None"""
    ErrorMessageBox(message).exec()


def information_dialog(title: str, message: str) -> None:
    """Create an informational dialog QDialog window with title and message.

    :param title:
    :type title: str
    :param message:
    :type message: str
    :return: None"""
    InformationDialog(title, message).exec()


# TODO: Broken
def display_metadata() -> None:
    """Display metadata in window or terminal. Internally, uses sitk.GetMetaData, which doesn't return
    all metadata (e.g., doesn't return spacing values whereas sitk.GetSpacing does).

    Typically, this returns less metadata for NRRD than for NIfTI.

    :return: None"""
    if not len(global_vars.IMAGE_DICT):
        print("Can't print metadata when there's no image!")
        return
    message: str = pprint.pformat(get_curr_metadata())
    if settings.DISPLAY_ADVANCED_MENU_MESSAGES_IN_TERMINAL:
        print(message)
    else:
        information_dialog("Metadata", message)


def display_dimensions() -> None:
    """Display current image's dimensions in window or terminal.

    :return: None"""
    if not len(global_vars.IMAGE_DICT):
        print("Can't print dimensions when there's no image!")
        return
    message: str = pprint.pformat(get_curr_image().GetSize())
    if settings.DISPLAY_ADVANCED_MENU_MESSAGES_IN_TERMINAL:
        print(message)
    else:
        information_dialog("Dimensions", message)


# TODO: If updating img_helpers.get_properties(), this needs to be slightly adjusted!
def display_properties() -> None:
    """Display properties in window or terminal.

    Internally, the properties tuple is a tuple of values only and doesn't contain
    field names. This function creates a dictionary with field names for printing. But the dictionary
    doesn't exist in the program.

    :return: None"""
    if not len(global_vars.IMAGE_DICT):
        print("No loaded image!")
        return
    curr_properties: tuple = get_curr_properties_tuple()
    fields: tuple = ("center of rotation", "dimensions", "spacing")
    if len(fields) != len(curr_properties):
        print(
            "Update NeuroRuler/GUI/main.print_properties() !\nNumber of fields and number of properties don't match."
        )
        exit(1)
    # Pretty sure the dict(zip(...)) goes through fields in alphabetical order
    message: str = pprint.pformat(dict(zip(fields, curr_properties)))
    if settings.DISPLAY_ADVANCED_MENU_MESSAGES_IN_TERMINAL:
        print(message)
    else:
        information_dialog("Properties", message)


def display_direction() -> None:
    """Display current image's direction in window or terminal.

    :return: None"""
    if not len(global_vars.IMAGE_DICT):
        print("Can't print direction when there's no image!")
        return
    message: str = pprint.pformat(get_curr_image().GetDirection())
    if settings.DISPLAY_ADVANCED_MENU_MESSAGES_IN_TERMINAL:
        print(message)
    else:
        information_dialog("Direction", message)


def display_spacing() -> None:
    """Display current image's spacing in window or terminal.

    :return: None"""
    if not len(global_vars.IMAGE_DICT):
        print("Can't print spacing when there's no image!")
        return
    message: str = pprint.pformat(get_curr_image().GetSpacing())
    if settings.DISPLAY_ADVANCED_MENU_MESSAGES_IN_TERMINAL:
        print(message)
    else:
        information_dialog("Spacing", message)


def main() -> None:
    """Main entrypoint of GUI."""
    # This import can't go at the top of the file
    # because gui.py.parse_gui_cli() has to set THEME_NAME before the import occurs
    # This imports globally
    # For example, NeuroRuler/GUI/helpers.py can access resource files without having to import there
    importlib.import_module(f"NeuroRuler.GUI.themes.{settings.THEME_NAME}.resources")

    app = QApplication(sys.argv)

    # On macOS, sets the application logo in the dock (but no window icon on macOS)
    # TODO
    # On Windows, sets the window icon at the top left of the window (but no dock icon on Windows)
    app.setWindowIcon(QIcon(str(PATH_TO_NR_LOGO)))

    # TODO: Put arrow buttons on the left and right endpoints of the sliders
    # These arrow buttons already show up if commenting in app.setStyle("Fusion")
    # And commenting out with open stylesheet and app.setStyleSheet
    # We should figure out how to get arrow buttons on sliders for (+, -) 1 precise adjustments.
    # Currently, the sliders allow this (left click on the left or right end), but the arrow buttons
    # are not in the GUI.
    # app.setStyle("Fusion")

    MAIN_WINDOW: MainWindow = MainWindow()

    with open(constants.THEME_DIR / settings.THEME_NAME / "stylesheet.qss", "r") as f:
        MAIN_WINDOW.setStyleSheet(f.read())

    # Non-zero min width and height is needed to prevent
    # this bug https://github.com/NIRALUser/NeuroRuler/issues/42
    # However, this also seems to affect startup GUI size or at least GUI element spacing
    MAIN_WINDOW.setMinimumSize(QSize(1, 1))
    MAIN_WINDOW.resize(
        int(settings.STARTUP_WIDTH_RATIO * constants.PRIMARY_MONITOR_DIMENSIONS[0]),
        int(settings.STARTUP_HEIGHT_RATIO * constants.PRIMARY_MONITOR_DIMENSIONS[1]),
    )

    MAIN_WINDOW.show()

    try:
        # sys.exit will cause a bug when running from terminal
        # After importing the GUI runner function from __init__, clicking the close window button
        # (not the menu button) will not close the window
        # because the Python process wouldn't end
        os._exit(app.exec())
    except:
        if settings.DEBUG:
            print("Exiting")


if __name__ == "__main__":
    import NeuroRuler.utils.parser as parser

    parser.parse_gui_config()
    parser.parse_gui_cli()
    main()

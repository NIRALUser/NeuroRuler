"""Defines MainWindow and main(), the entrypoint of the GUI.

Loads `src/GUI/mainwindow.ui`, made in QtDesigner.

Loads `.qss` stylesheets and `resources.py` (icons) files, generated
by BreezeStyleSheets. Our fork of the repo: https://github.com/COMP523TeamD/BreezeStyleSheets.

If adding a new GUI element (in the GUI or in the menubar, whatever), you'll have to modify
modify __init__ and settings_view_toggle.

Edge cases: If this element should be disabled after enable_elements or enabled after disable_elements,
then you will need to modify those."""


import importlib
import sys
import webbrowser
from pathlib import Path
from typing import Union
from enum import Enum

import SimpleITK as sitk
import numpy as np

from PySide6 import QtGui, QtCore
from PySide6.QtGui import QPixmap, QAction
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QMenu,
    QMenuBar,
    QWidgetAction,
    QWidget,
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt

from src.GUI.ui_mainwindow import Ui_MainWindow

import qimage2ndarray
import pprint

# The regular Python 3.7+ dict maintains insertion order.
# This is used only in print_properties()
from collections import OrderedDict

from src.utils.constants import View, ThresholdFilter
import src.utils.constants as constants

# Note, do not use imports like
# from src.utils.global_vars import IMAGE_DICT
# This would make the global variables not work
import src.utils.global_vars as global_vars
import src.utils.imgproc as imgproc
import src.utils.user_settings as user_settings
from src.GUI.helpers import (
    string_to_QColor,
    mask_QImage,
)

from src.utils.img_helpers import (
    initialize_globals,
    update_image_groups,
    get_curr_image,
    get_curr_image_size,
    get_curr_rotated_slice,
    get_curr_smooth_slice,
    get_curr_metadata,
    curr_binary_filter,
    curr_otsu_filter,
    get_curr_physical_units,
    get_curr_path,
    get_curr_properties_tuple,
    get_middle_dimension,
)

import src.utils.img_helpers as img_helpers


LOADER: QUiLoader = QUiLoader()
PATH_TO_HCT_LOGO: Path = Path("src") / "GUI" / "static" / "hct_logo.png"

DEFAULT_CIRCUMFERENCE_LABEL_TEXT: str = "Calculated Circumference: N/A"
DEFAULT_IMAGE_PATH_LABEL_TEXT: str = "Image path"
GITHUB_LINK: str = "https://github.com/COMP523TeamD/HeadCircumferenceTool"
DOCUMENTATION_LINK: str = "https://headcircumferencetool.readthedocs.io/en/latest/"
DEFAULT_IMAGE_TEXT: str = "Select images using File > Open!"
DEFAULT_IMAGE_NUM_LABEL_TEXT: str = "Image 0 of 0"
DEFAULT_IMAGE_STATUS_TEXT: str = "Image path is displayed here."

# We assume units are millimeters if we can't find units in metadata
MESSAGE_TO_SHOW_IF_UNITS_NOT_FOUND: str = "millimeters (mm)"


class MainWindow(QMainWindow):
    """Main window of the application.

    Settings mode and circumference mode."""

    def __init__(self):
        """Load main.ui file and connect GUI events to methods/functions.

        Sets window title and icon."""
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle("Head Circumference Tool")
        self.setWindowIcon(QtGui.QIcon(str(PATH_TO_HCT_LOGO)))

        self.ui.action_open.triggered.connect(lambda: self.browse_files(False))
        self.ui.action_add_images.triggered.connect(lambda: self.browse_files(True))
        self.ui.action_remove_image.triggered.connect(self.remove_curr_img)
        self.ui.action_exit.triggered.connect(exit)
        self.ui.action_github.triggered.connect(lambda: webbrowser.open(GITHUB_LINK))
        self.ui.action_documentation.triggered.connect(
            lambda: webbrowser.open(DOCUMENTATION_LINK)
        )
        self.ui.action_test_stuff.triggered.connect(self.test_stuff)
        self.ui.action_print_metadata.triggered.connect(print_metadata)
        self.ui.action_print_dimensions.triggered.connect(print_dimensions)
        self.ui.action_print_properties.triggered.connect(print_properties)
        self.ui.action_print_direction.triggered.connect(print_direction)
        self.ui.action_print_spacing.triggered.connect(print_spacing)
        self.ui.action_export_png.triggered.connect(
            lambda: self.export_curr_slice_as_img("png")
        )
        self.ui.action_export_jpg.triggered.connect(
            lambda: self.export_curr_slice_as_img("jpg")
        )
        self.ui.action_export_bmp.triggered.connect(
            lambda: self.export_curr_slice_as_img("bmp")
        )
        self.ui.action_export_ppm.triggered.connect(
            lambda: self.export_curr_slice_as_img("ppm")
        )
        self.ui.action_export_xbm.triggered.connect(
            lambda: self.export_curr_slice_as_img("xbm")
        )
        self.ui.action_export_xpm.triggered.connect(
            lambda: self.export_curr_slice_as_img("xpm")
        )
        self.ui.next_button.clicked.connect(self.next_img)
        self.ui.previous_button.clicked.connect(self.previous_img)
        self.ui.apply_button.clicked.connect(self.settings_export_view_toggle)
        self.ui.x_slider.valueChanged.connect(self.rotate_x)
        self.ui.y_slider.valueChanged.connect(self.rotate_y)
        self.ui.z_slider.valueChanged.connect(self.rotate_z)
        self.ui.slice_slider.valueChanged.connect(self.slice_update)
        self.ui.reset_button.clicked.connect(self.reset_settings)
        self.ui.smoothing_preview_button.clicked.connect(self.render_smooth_slice)
        self.ui.otsu_radio_button.clicked.connect(self.disable_binary_if_using_otsu)
        self.ui.binary_radio_button.clicked.connect(self.enable_binary_if_using_binary)
        self.ui.threshold_preview_button.clicked.connect(self.render_threshold)
        self.ui.x_view_radio_button.clicked.connect(self.update_view)
        self.ui.y_view_radio_button.clicked.connect(self.update_view)
        self.ui.z_view_radio_button.clicked.connect(self.update_view)
        self.show()

    def enable_elements(self) -> None:
        """Called after File > Open.

        Enables GUI elements. Explicitly disables some (e.g., Export CSV menu item).
        """
        # findChildren searches recursively by default
        for widget in self.findChildren(QWidget):
            widget.setEnabled(True)

        # Menu stuff
        for widget in self.findChildren(QAction):
            widget.setEnabled(True)

        self.ui.action_export_csv.setEnabled(not global_vars.SETTINGS_VIEW_ENABLED)

    def disable_binary_if_using_otsu(self) -> None:
        """Called when using Otsu filter
        
        Disable binary input box.
        """
        self.ui.upper_threshold_input.setEnabled(False)
        self.ui.lower_threshold_input.setEnabled(False)

    def enable_binary_if_using_binary(self) -> None:
        """Called when using Binary filter
        
        Restore binary input box.
        """
        self.ui.upper_threshold_input.setEnabled(True)
        self.ui.lower_threshold_input.setEnabled(True)

    def settings_export_view_toggle(self) -> None:
        """Called when clicking Apply (in settings mode) or Adjust (in circumference mode).

        Toggle SETTINGS_VIEW_ENABLED, change apply button text, render stuff depending on the current mode.

        Enables/disables GUI elements depending on the value of SETTINGS_VIEW_ENABLED.
        """
        global_vars.SETTINGS_VIEW_ENABLED = not global_vars.SETTINGS_VIEW_ENABLED
        settings_view_enabled = global_vars.SETTINGS_VIEW_ENABLED
        if settings_view_enabled:
            self.ui.apply_button.setText("Apply")
            self.ui.circumference_label.setText(DEFAULT_CIRCUMFERENCE_LABEL_TEXT)
            # Render uncontoured slice after pressing adjust
            self.render_curr_slice()
        else:
            self.update_smoothing_settings()
            self.update_binary_filter_settings()
            self.ui.apply_button.setText("Adjust")
            # Ignore the type annotation error here.
            # render_curr_slice() must return np.ndarray since not settings_view_enabled here
            binary_contour_slice: np.ndarray = self.render_curr_slice()
            self.render_circumference(binary_contour_slice)

        self.ui.action_open.setEnabled(settings_view_enabled)
        self.ui.action_add_images.setEnabled(settings_view_enabled)
        self.ui.action_remove_image.setEnabled(settings_view_enabled)
        self.ui.x_slider.setEnabled(settings_view_enabled)
        self.ui.y_slider.setEnabled(settings_view_enabled)
        self.ui.z_slider.setEnabled(settings_view_enabled)
        self.ui.slice_slider.setEnabled(settings_view_enabled)
        self.ui.x_rotation_label.setEnabled(settings_view_enabled)
        self.ui.y_rotation_label.setEnabled(settings_view_enabled)
        self.ui.z_rotation_label.setEnabled(settings_view_enabled)
        self.ui.slice_num_label.setEnabled(settings_view_enabled)
        self.ui.reset_button.setEnabled(settings_view_enabled)
        self.ui.smoothing_preview_button.setEnabled(settings_view_enabled)
        self.ui.otsu_radio_button.setEnabled(settings_view_enabled)
        self.ui.binary_radio_button.setEnabled(settings_view_enabled)
        self.ui.lower_threshold.setEnabled(settings_view_enabled)
        self.ui.lower_threshold_input.setEnabled(settings_view_enabled)
        self.ui.upper_threshold.setEnabled(settings_view_enabled)
        self.ui.upper_threshold_input.setEnabled(settings_view_enabled)
        self.ui.threshold_preview_button.setEnabled(settings_view_enabled)
        self.ui.action_export_csv.setEnabled(not settings_view_enabled)
        self.ui.circumference_label.setEnabled(not settings_view_enabled)
        self.ui.export_button.setEnabled(not settings_view_enabled)
        self.ui.smoothing_preview_button.setEnabled(settings_view_enabled)
        self.ui.conductance_parameter_label.setEnabled(settings_view_enabled)
        self.ui.conductance_parameter_input.setEnabled(settings_view_enabled)
        self.ui.smoothing_iterations_label.setEnabled(settings_view_enabled)
        self.ui.smoothing_iterations_input.setEnabled(settings_view_enabled)
        self.ui.time_step_label.setEnabled(settings_view_enabled)
        self.ui.time_step_input.setEnabled(settings_view_enabled)
        self.ui.x_view_radio_button.setEnabled(settings_view_enabled)
        self.ui.y_view_radio_button.setEnabled(settings_view_enabled)
        self.ui.z_view_radio_button.setEnabled(settings_view_enabled)

    def disable_elements(self) -> None:
        """Called when the list is now empty, i.e. just removed from list of length 1.

        Explicitly enables elements that should never be disabled and sets default text.
        """
        central_widget = self.findChildren(QWidget, "centralwidget")[0]
        menubar = self.menuBar()

        for gui_element in central_widget.findChildren(QWidget):
            gui_element.setEnabled(False)

        # findChildren searches recursively by default
        for menu in menubar.findChildren(QMenu):
            for action in menu.actions():
                action.setEnabled(False)

        self.ui.action_open.setEnabled(True)
        self.ui.circumference_label.setText(DEFAULT_CIRCUMFERENCE_LABEL_TEXT)
        self.ui.image.setEnabled(True)
        self.ui.image.clear()
        self.ui.image.setText(DEFAULT_IMAGE_TEXT)
        self.ui.image.setStatusTip(DEFAULT_IMAGE_STATUS_TEXT)
        self.ui.image_path_label.setText(DEFAULT_IMAGE_PATH_LABEL_TEXT)
        self.ui.image_num_label.setText(DEFAULT_IMAGE_NUM_LABEL_TEXT)
        self.ui.apply_button.setText("Apply")
        self.ui.z_view_radio_button.setChecked(True)

    def browse_files(self, extend: bool) -> None:
        """Called after File > Open or File > Add Images.

        If `extend`, then `IMAGE_GROUPS` will be updated with new images.

        Else, `IMAGE_GROUPS` will be cleared and
        (re)initialized (e.g. when choosing files for the first time or re-opening).

        Since IMAGE_DICT is a reference to an image dict in IMAGE_GROUPS, IMAGE_DICT is also cleared and
        (re)initialized.

        Opens file menu.

        Renders various elements depending on the value of `extend`.

        :param extend: Whether to clear IMAGE_GROUPS and (re)initialize or add images to it. Determines which GUI elements are rendered.
        :type extend: bool
        :return: None"""
        file_filter: str = "MRI images " + str(constants.SUPPORTED_EXTENSIONS).replace(
            "'", ""
        ).replace(",", "")

        files = QFileDialog.getOpenFileNames(
            self, "Open files", str(user_settings.FILE_BROWSER_START_DIR), file_filter
        )

        # list[str]
        path_list = files[0]
        if len(path_list) == 0:
            return

        # Convert to list[Path]. Slight inefficiency but worth.
        path_list = list(map(Path, path_list))

        if not extend:
            initialize_globals(path_list)
            self.render_all_sliders()
            self.enable_elements()
            self.render_image_num_and_path()
            self.orient_curr_image(global_vars.VIEW)
            self.render_curr_slice()
        else:
            # Doesn't need to re-render sliders to set max value of slice slider.
            # update_image_groups does not change the batch.
            # Therefore, max value of slice slider does not change.
            # Must render image_num.
            # Does not need to render current slice. Images are added to the end of the dict.
            # And adding duplicate key doesn't change key order.
            self.enable_elements()
            update_image_groups(path_list)
            self.render_image_num_and_path()

    def update_view(self) -> None:
        """Renders view."""

        if (
            self.ui.x_view_radio_button.isChecked()
            and global_vars.VIEW != constants.View.X
        ):
            global_vars.VIEW = constants.View.X
            self.ui.y_view_radio_button.setChecked(False)
            self.ui.z_view_radio_button.setChecked(False)

        elif (
            self.ui.y_view_radio_button.isChecked()
            and global_vars.VIEW != constants.View.Y
        ):
            global_vars.VIEW = constants.View.Y
            self.ui.x_view_radio_button.setChecked(False)
            self.ui.z_view_radio_button.setChecked(False)

        else:
            global_vars.VIEW = constants.View.Z
            self.ui.x_view_radio_button.setChecked(False)
            self.ui.y_view_radio_button.setChecked(False)

        self.orient_curr_image(global_vars.VIEW)
        self.render_curr_slice()

    def set_view_z(self) -> None:
        global_vars.VIEW = constants.View.Z
        self.ui.x_view_radio_button.setChecked(False)
        self.ui.y_view_radio_button.setChecked(False)
        self.ui.z_view_radio_button.setChecked(True)

    def render_curr_slice(self) -> Union[np.ndarray, None]:
        """Resamples the currently selected image using its rotation and slice settings,
        then renders the resulting slice in the GUI.

        DOES NOT set text for `image_num_label` and file path labels.

        If `not SETTINGS_VIEW_ENABLED`, also calls `imgproc.contour()` and outlines
        the contour of the QImage (mutating it).

        Additionally, also returns a view of the binary contoured slice if `not SETTINGS_VIEW_ENABLED`.
        This saves work when computing circumference.

        :return: np.ndarray if `not SETTINGS_VIEW_ENABLED` else None
        :rtype: np.ndarray or None"""

        if not global_vars.SETTINGS_VIEW_ENABLED:
            self.set_view_z()

        rotated_slice: sitk.Image = get_curr_rotated_slice()

        slice_np: np.ndarray = sitk.GetArrayFromImage(rotated_slice)

        q_img = qimage2ndarray.array2qimage(slice_np, normalize=True)

        rv_dummy_var: np.ndarray = np.zeros(0)

        if not global_vars.SETTINGS_VIEW_ENABLED:
            if self.ui.otsu_radio_button.isChecked():
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
                string_to_QColor(user_settings.CONTOUR_COLOR),
            )

        elif global_vars.VIEW != constants.View.Z:
            z_indicator: np.ndarray = np.zeros(slice_np.shape)
            z_indicator[get_curr_image_size()[2] - global_vars.SLICE - 1, :] = 1
            mask_QImage(
                q_img,
                np.transpose(z_indicator),
                string_to_QColor(user_settings.CONTOUR_COLOR),
            )

        q_pixmap: QPixmap = QPixmap(q_img)

        self.ui.image.setPixmap(q_pixmap)

        if not global_vars.SETTINGS_VIEW_ENABLED:
            return rv_dummy_var

    def update_smoothing_settings(self) -> None:
        """Updates global smoothing settings."""

        conductance: str = self.ui.conductance_parameter_input.displayText()
        try:
            global_vars.CONDUCTANCE_PARAMETER = float(conductance)
        except ValueError:
            if user_settings.DEBUG:
                print("Conductance must be a float!")
        self.ui.conductance_parameter_input.setText(
            str(global_vars.CONDUCTANCE_PARAMETER)
        )
        self.ui.conductance_parameter_input.setPlaceholderText(
            str(global_vars.CONDUCTANCE_PARAMETER)
        )
        global_vars.SMOOTHING_FILTER.SetConductanceParameter(
            global_vars.CONDUCTANCE_PARAMETER
        )

        iterations: str = self.ui.smoothing_iterations_input.displayText()
        try:
            global_vars.CONDUCTANCE_PARAMETER = int(iterations)
        except ValueError:
            if user_settings.DEBUG:
                print("Iterations must be an integer!")
        self.ui.smoothing_iterations_input.setText(
            str(global_vars.SMOOTHING_ITERATIONS)
        )
        self.ui.smoothing_iterations_input.setPlaceholderText(
            str(global_vars.SMOOTHING_ITERATIONS)
        )
        global_vars.SMOOTHING_FILTER.SetNumberOfIterations(
            global_vars.SMOOTHING_ITERATIONS
        )

        time_step: str = self.ui.time_step_input.displayText()
        try:
            global_vars.TIME_STEP = float(time_step)
        except ValueError:
            if user_settings.DEBUG:
                print("Time step must be a float!")
        self.ui.time_step_input.setText(str(global_vars.TIME_STEP))
        self.ui.time_step_input.setPlaceholderText(str(global_vars.TIME_STEP))
        global_vars.SMOOTHING_FILTER.SetTimeStep(global_vars.TIME_STEP)

    def render_smooth_slice(self) -> Union[np.ndarray, None]:
        """Renders smooth slice in GUI. Allows user to preview result of smoothing settings."""
        self.update_smoothing_settings()

        self.set_view_z()

        smooth_slice: sitk.Image = get_curr_smooth_slice()

        slice_np: np.ndarray = sitk.GetArrayFromImage(smooth_slice)

        q_img = qimage2ndarray.array2qimage(slice_np, normalize=True)

        q_pixmap: QPixmap = QPixmap(q_img)

        self.ui.image.setPixmap(q_pixmap)

    def update_binary_filter_settings(self) -> None:
        """Updates global binary filter settings."""

        lower_threshold: str = self.ui.lower_threshold_input.displayText()
        try:
            float(lower_threshold)
            global_vars.LOWER_THRESHOLD = float(lower_threshold)
        except ValueError:
            None
        self.ui.lower_threshold_input.setText(str(global_vars.LOWER_THRESHOLD))
        self.ui.lower_threshold_input.setPlaceholderText(
            str(global_vars.LOWER_THRESHOLD)
        )
        global_vars.BINARY_THRESHOLD_FILTER.SetLowerThreshold(
            global_vars.LOWER_THRESHOLD
        )

        upper_threshold: str = self.ui.upper_threshold_input.displayText()
        try:
            float(upper_threshold)
            global_vars.UPPER_THRESHOLD = float(upper_threshold)
        except ValueError:
            None
        self.ui.upper_threshold_input.setText(str(global_vars.UPPER_THRESHOLD))
        self.ui.upper_threshold_input.setPlaceholderText(
            str(global_vars.UPPER_THRESHOLD)
        )
        global_vars.BINARY_THRESHOLD_FILTER.SetUpperThreshold(
            global_vars.UPPER_THRESHOLD
        )

    def render_threshold(self) -> Union[np.ndarray, None]:
        """Render filtered image slice on UI"""
        if self.ui.otsu_radio_button.isChecked():
            filter_img: sitk.Image = curr_otsu_filter()
        else:
            self.update_binary_filter_settings()
            filter_img: sitk.Image = curr_binary_filter()

        slice_np: np.ndarray = sitk.GetArrayFromImage(filter_img)

        q_img = qimage2ndarray.array2qimage(slice_np, normalize=True)

        q_pixmap: QPixmap = QPixmap(q_img)

        self.ui.image.setPixmap(q_pixmap)

    def render_circumference(self, binary_contour_slice: np.ndarray) -> None:
        """Called after pressing Apply or when
        (not SETTINGS_VIEW_ENABLED and (pressing Next or Previous or Remove Image))

        Computes circumference from binary_contour_slice and renders circumference label.

        binary_contour_slice is always the return value of render_curr_slice since render_curr_slice must have
        already been called. If calling this function, render_curr_slice must have been called first.

        :param binary_contour_slice: Result of previously calling render_curr_slice when `not SETTINGS_VIEW_ENABLED`
        :type binary_contour_slice: np.ndarray
        :return: None
        :rtype: None"""
        if global_vars.SETTINGS_VIEW_ENABLED:
            raise Exception(
                "Rendering circumference label when global_vars.SETTINGS_VIEW_ENABLED"
            )
        units: Union[str, None] = get_curr_physical_units()
        circumference: float = imgproc.length_of_contour(binary_contour_slice)
        self.ui.circumference_label.setText(
            f"Calculated Circumference: {round(circumference, constants.NUM_DIGITS_TO_ROUND_TO)} {units if units is not None else MESSAGE_TO_SHOW_IF_UNITS_NOT_FOUND}"
        )

    def render_image_num_and_path(self) -> None:
        """Set image_num_label, image_path_label, and status tip of the image.

        Called when pressing Next or Previous (next_img, prev_img), and after File > Open (browse_files).

        Also called when removing an image.

        :return: None"""
        self.ui.image_num_label.setText(
            f"Image {global_vars.CURR_IMAGE_INDEX + 1} of {len(global_vars.IMAGE_DICT)}"
        )
        self.ui.image_path_label.setText(str(get_curr_path().name))
        self.ui.image_path_label.setStatusTip(str(get_curr_path()))
        self.ui.image.setStatusTip(str(get_curr_path()))

    def render_all_sliders(self) -> None:
        """Sets all slider values to the global rotation and slice values.
        Also updates maximum value of slice slider.

        Called on reset. Will need to be called when updating batch index, if we implement this.

        Not called when the user updates a slider.

        Also updates rotation and slice num labels."""
        self.ui.x_slider.setValue(global_vars.THETA_X)
        self.ui.y_slider.setValue(global_vars.THETA_Y)
        self.ui.z_slider.setValue(global_vars.THETA_Z)
        self.ui.slice_slider.setMaximum(get_curr_image().GetSize()[2] - 1)
        self.ui.slice_slider.setValue(global_vars.SLICE)
        self.ui.x_rotation_label.setText(f"X rotation: {global_vars.THETA_X}°")
        self.ui.y_rotation_label.setText(f"Y rotation: {global_vars.THETA_Y}°")
        self.ui.z_rotation_label.setText(f"Z rotation: {global_vars.THETA_Z}°")
        self.ui.slice_num_label.setText(f"Slice: {global_vars.SLICE}")

    # TODO: Due to the images now being a dict, we can
    # easily let the user remove a range of images if they want
    def remove_curr_img(self) -> None:
        """Called after File > Remove File.

        Removes current image from `IMAGE_DICT`. Since `IMAGE_DICT` is a reference to an image dict
        in `IMAGE_GROUPS`, it's removed from `IMAGE_GROUPS` as well.

        :returns: None"""
        img_helpers.del_curr_img()

        if len(global_vars.IMAGE_DICT) == 0:
            self.disable_elements()
            return

        binary_contour_or_none: Union[np.ndarray, None] = self.render_curr_slice()
        self.render_image_num_and_path()

        if not global_vars.SETTINGS_VIEW_ENABLED:
            # Ignore the type annotation error. binary_contour_or_none must be binary_contour since not SETTINGS_VIEW_ENABLED
            self.render_circumference(binary_contour_or_none)

    def next_img(self):
        """Called when Next button is clicked.

        Advance index and render."""
        img_helpers.next_img()
        self.orient_curr_image(global_vars.VIEW)
        binary_contour_or_none: Union[np.ndarray, None] = self.render_curr_slice()
        self.render_image_num_and_path()

        if not global_vars.SETTINGS_VIEW_ENABLED:
            # Ignore the type annotation error. binary_contour_or_none must be binary_contour since not SETTINGS_VIEW_ENABLED
            self.render_circumference(binary_contour_or_none)

    def previous_img(self):
        """Called when Previous button is clicked.

        Decrement index and render."""
        img_helpers.previous_img()
        self.orient_curr_image(global_vars.VIEW)
        binary_contour_or_none: Union[np.ndarray, None] = self.render_curr_slice()
        self.render_image_num_and_path()

        if not global_vars.SETTINGS_VIEW_ENABLED:
            # Ignore the type annotation error. binary_contour_or_none must be binary_contour since not SETTINGS_VIEW_ENABLED
            self.render_circumference(binary_contour_or_none)

    def rotate_x(self):
        """Called when the user updates the x slider.

        Render image and set `x_rotation_label`."""
        x_slider_val: int = self.ui.x_slider.value()
        global_vars.THETA_X = x_slider_val
        self.render_curr_slice()
        self.ui.x_rotation_label.setText(f"X rotation: {x_slider_val}°")

    def rotate_y(self):
        """Called when the user updates the y slider.

        Render image and set `y_rotation_label`."""
        y_slider_val: int = self.ui.y_slider.value()
        global_vars.THETA_Y = y_slider_val
        self.render_curr_slice()
        self.ui.y_rotation_label.setText(f"Y rotation: {y_slider_val}°")

    def rotate_z(self):
        """Called when the user updates the z slider.

        Render image and set `z_rotation_label`."""
        z_slider_val: int = self.ui.z_slider.value()
        global_vars.THETA_Z = z_slider_val
        self.render_curr_slice()
        self.ui.z_rotation_label.setText(f"Z rotation: {z_slider_val}°")

    def slice_update(self):
        """Called when the user updates the slice slider.

        Render image and set `slice_num_label`."""
        slice_slider_val: int = self.ui.slice_slider.value()
        global_vars.SLICE = slice_slider_val
        self.render_curr_slice()
        self.ui.slice_num_label.setText(f"Slice: {slice_slider_val}")

    def reset_settings(self):
        """Called when Reset is clicked.

        Resets rotation values to 0 and slice num to the default `int((z-1)/2)`
        for the current image, then renders current image and sliders."""
        global_vars.THETA_X = 0
        global_vars.THETA_Y = 0
        global_vars.THETA_Z = 0
        global_vars.SLICE = get_middle_dimension(get_curr_image(), View.Z)
        self.render_curr_slice()
        self.render_all_sliders()

    def test_stuff(self) -> None:
        """Connected to Debug > Test stuff. Dummy button and function for easily testing stuff.

        Assume that anything you put here will be overwritten freely."""
        self.ui.image.setPixmap(QPixmap(f":/{user_settings.THEME_NAME}/help.svg"))
        self.ui.image.setStatusTip(
            "This is intentional, if it's a question mark then that's good :), means we can display icons"
        )

    # TODO: File name should also include circumference when not SETTINGS_VIEW_ENABLED?
    def export_curr_slice_as_img(self, extension: str):
        """Called when an Export as image menu item is clicked.

        Exports `self.image` to `settings.IMG_DIR`. Thus, calling this when `SETTINGS_VIEW_ENABLED` will
        save a non-contoured image. Calling this when `not SETTINGS_VIEW_ENABLED` will save a contoured
        image.

        Filename has format <file_name>_[contoured_]<theta_x>_<theta_y>_<theta_z>_<slice_num>.<extension>

        contoured_ will be in the name if `not SETTINGS_VIEW_ENABLED`.

        Supported formats in this function are the ones supported by QPixmap,
        namely BMP, JPG, JPEG, PNG, PPM, XBM, XPM.

        :param extension: BMP, JPG, JPEG, PNG, PPM, XBM, XPM
        :type extension: str
        :return: `None`"""
        file_name = (
            global_vars.CURR_IMAGE_INDEX + 1
            if user_settings.EXPORTED_FILE_NAMES_USE_INDEX
            else get_curr_path().name
        )
        path: str = str(
            user_settings.IMG_DIR
            / f"{file_name}_{'contoured_' if not global_vars.SETTINGS_VIEW_ENABLED else ''}{global_vars.THETA_X}_{global_vars.THETA_Y}_{global_vars.THETA_Z}_{global_vars.SLICE}.{extension}"
        )
        self.ui.image.pixmap().save(path, extension)

    def orient_curr_image(self, view: Enum) -> None:
        """Mutate the current image by applying ORIENT_FILTER on it.

        The orientation applied depends on the view. See img_helpers.orient_curr_image.
        """
        img_helpers.orient_curr_image(view)


def print_metadata() -> None:
    """Print current image's metadata to terminal. Internally, uses sitk.GetMetaData, which doesn't return
    all metadata (e.g., doesn't return spacing values whereas sitk.GetSpacing does).

    Typically, this returns less metadata for NRRD than for NIfTI."""

    if not len(global_vars.IMAGE_DICT):
        print("Can't print metadata when there's no image!")
        return
    pprint.pprint(get_curr_metadata())


def print_dimensions() -> None:
    """Print currently displayed image's dimensions to terminal."""
    if not len(global_vars.IMAGE_DICT):
        print("Can't print dimensions when there's no image!")
        return
    print(get_curr_image().GetSize())


# TODO: If updating img_helpers.get_properties(), this needs to be slightly adjusted!
def print_properties() -> None:
    """Print current batch's properties to terminal.

    Internally, the properties tuple is a tuple of values only and doesn't contain
    field names. This function creates a dictionary with field names for printing. But the dictionary
    doesn't exist in the program."""
    if not len(global_vars.IMAGE_DICT):
        print("No loaded image!")
        return
    curr_properties: tuple = get_curr_properties_tuple()
    fields: tuple = ("dimensions", "center of rotation", "spacing")
    if len(fields) != len(curr_properties):
        print(
            "Update src/GUI/main.print_properties() !\nNumber of fields and number of properties don't match."
        )
        exit(1)
    pprint.pprint(OrderedDict(zip(fields, curr_properties)))


def print_direction() -> None:
    """Print current image's dimensions to terminal."""
    if not len(global_vars.IMAGE_DICT):
        print("Can't print direction when there's no image!")
        return
    print(get_curr_image().GetDirection())


def print_spacing() -> None:
    if not len(global_vars.IMAGE_DICT):
        print("Can't print spacing when there's no image!")
        return
    print(get_curr_image().GetSpacing())


def main() -> None:
    """Main entrypoint of GUI."""
    # This import can't go at the top of the file
    # because gui.py.parse_gui_cli() has to set THEME_NAME before the import occurs
    importlib.import_module(f"src.GUI.themes.{user_settings.THEME_NAME}.resources")

    if not user_settings.IMG_DIR.exists():
        user_settings.IMG_DIR.mkdir()

    app = QApplication(sys.argv)

    # TODO: This puts arrow buttons on the left and right endpoints of the sliders
    # If the QSS below isn't loaded (i.e., comment out the below two lines)
    # We should figure out how to get arrow buttons on sliders for (+, -) 1 precise adjustments.
    # Currently, the sliders allow this (left click on the left or right end), but it's not obvious in the GUI.

    # app.setStyle('Fusion')

    with open(
        constants.THEME_DIR / user_settings.THEME_NAME / f"stylesheet.qss", "r"
    ) as f:
        app.setStyleSheet(f.read())

    MAIN_WINDOW = MainWindow()
    MAIN_WINDOW.setMinimumWidth(
        int(user_settings.MIN_WIDTH_RATIO * user_settings.PRIMARY_MONITOR_DIMENSIONS[0])
    )
    MAIN_WINDOW.setMinimumHeight(
        int(
            user_settings.MIN_HEIGHT_RATIO * user_settings.PRIMARY_MONITOR_DIMENSIONS[1]
        )
    )

    MAIN_WINDOW.setMaximumWidth(
        int(user_settings.MAX_WIDTH_RATIO * user_settings.PRIMARY_MONITOR_DIMENSIONS[0])
    )
    MAIN_WINDOW.setMaximumHeight(
        int(
            user_settings.MAX_HEIGHT_RATIO * user_settings.PRIMARY_MONITOR_DIMENSIONS[1]
        )
    )

    try:
        sys.exit(app.exec())
    except:
        if user_settings.DEBUG:
            print("Exiting")


if __name__ == "__main__":
    import src.utils.parser as parser

    parser.parse_json()
    parser.parse_gui_cli()
    main()

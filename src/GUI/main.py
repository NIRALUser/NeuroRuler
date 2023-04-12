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

import SimpleITK as sitk
import numpy as np

from PyQt6 import QtGui, QtCore
from PyQt6.QtGui import QPixmap, QAction, QImage, QIcon
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
    sitk_slice_to_qimage,
    ErrorMessageBox,
    InformationMessageBox,
    InformationDialog,
)

from src.utils.img_helpers import (
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
    get_curr_properties_tuple,
    get_middle_dimension,
)

import src.utils.img_helpers as img_helpers


PATH_TO_UI_FILE: Path = Path("src") / "GUI" / "mainwindow.ui"
PATH_TO_HCT_LOGO: Path = Path("src") / "GUI" / "static" / "hct_logo.png"

SETTINGS_VIEW_ENABLED: bool = True
"""Whether the user is able to adjust settings (settings screen) or not
(circumference and contoured image screen)."""

DEFAULT_CIRCUMFERENCE_LABEL_TEXT: str = "Calculated Circumference: N/A"
DEFAULT_IMAGE_PATH_LABEL_TEXT: str = "Image path"
GITHUB_LINK: str = "https://github.com/COMP523TeamD/HeadCircumferenceTool"
DOCUMENTATION_LINK: str = "https://headcircumferencetool.readthedocs.io/en/latest/"
DEFAULT_IMAGE_TEXT: str = "Select images using File > Open!"
DEFAULT_IMAGE_NUM_LABEL_TEXT: str = "Image 0 of 0"
DEFAULT_IMAGE_STATUS_TEXT: str = "Image path is displayed here."

# We assume units are millimeters if we can't find units in metadata
MESSAGE_TO_SHOW_IF_UNITS_NOT_FOUND: str = "millimeters (mm)"

UNSCALED_QPIXMAP: QPixmap
"""Unscaled QPixmap from which the scaled version is rendered in the GUI.

When any slice (rotated, smoothed, previewed) is rendered from an unscaled QImage, this variable is set to the
QPixmap generated from that unscaled QImage.

This variable will not change on resizeEvent. resizeEvent will scale this. Otherwise, if scaling
self.image's pixmap (which is already scaled), there would be loss of detail."""


class MainWindow(QMainWindow):
    """Main window of the application.

    Settings mode and circumference mode."""

    def __init__(self):
        """Load main file and connect GUI events to methods/functions.

        Sets window title and icon."""
        super(MainWindow, self).__init__()
        loadUi(str(PATH_TO_UI_FILE), self)

        self.setWindowTitle("Head Circumference Tool")

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
                'Credit to Jesse Wei, Madison Lester, Peifeng "Hank" He, Eric Schneider, and Martin Styner.',
            )
        )
        self.action_test_stuff.triggered.connect(self.test_stuff)
        self.action_print_metadata.triggered.connect(display_metadata)
        self.action_print_dimensions.triggered.connect(display_dimensions)
        self.action_print_properties.triggered.connect(display_properties)
        self.action_print_direction.triggered.connect(display_direction)
        self.action_print_spacing.triggered.connect(display_spacing)
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
        self.show()

    def enable_elements(self) -> None:
        """Called after File > Open.

        Enables GUI elements. Explicitly disables some (e.g., Export CSV menu item and
        binary threshold inputs, since Otsu is default).
        """
        # findChildren searches recursively by default
        for widget in self.findChildren(QWidget):
            widget.setEnabled(True)

        # Menu stuff
        for widget in self.findChildren(QAction):
            widget.setEnabled(True)

        self.action_export_csv.setEnabled(not SETTINGS_VIEW_ENABLED)
        self.export_button.setEnabled(not SETTINGS_VIEW_ENABLED)
        self.disable_binary_threshold_inputs()

    def enable_binary_threshold_inputs(self) -> None:
        """Called when Binary filter button is clicked.

        Restore binary input box.
        """
        self.upper_threshold_input.setEnabled(True)
        self.lower_threshold_input.setEnabled(True)

    def settings_export_view_toggle(self) -> None:
        """Called when clicking Apply (in settings mode) or Adjust (in circumference mode).

        Toggle SETTINGS_VIEW_ENABLED, change apply button text, render stuff depending on the current mode.

        Enables/disables GUI elements depending on the value of SETTINGS_VIEW_ENABLED.
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

            self.update_smoothing_settings()
            self.update_binary_filter_settings()
            self.apply_button.setText("Adjust")
            # Ignore the type annotation warning here.
            # render_curr_slice() must return np.ndarray since not settings_view_enabled here
            binary_contour_slice: np.ndarray = self.render_curr_slice()
            self.render_circumference(binary_contour_slice)

        # TODO: Call enable_elements and then a disable method (code another one, and it'd be short)
        # If not settings_view_enabled
        self.action_open.setEnabled(settings_view_enabled)
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
        self.action_export_csv.setEnabled(not settings_view_enabled)
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
        """
        self.upper_threshold_input.setEnabled(False)
        self.lower_threshold_input.setEnabled(False)

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

    def browse_files(self, extend: bool) -> None:
        """Called after File > Open or File > Add Images.

        If `extend`, then `IMAGE_DICT` will be updated with new images.

        Else, `IMAGE_DICT` will be cleared and
        (re)initialized (e.g. when choosing files for the first time or re-opening).

        Opens file menu.

        Renders various elements depending on the value of `extend`.

        :param extend: Whether to clear IMAGE_DICT and (re)initialize or add images to it. Determines which GUI elements are rendered.
        :type extend: bool
        :return: None
        :rtype: None"""
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
        """Set global_vars.VIEW to View.Z and set the z radio button to checked."""
        global_vars.VIEW = constants.View.Z
        # TODO: Uncheck x and y are technically unnecessary since these 3 buttons in the view_button_group have
        # autoExclusive=True
        self.x_view_radio_button.setChecked(False)
        self.y_view_radio_button.setChecked(False)
        self.z_view_radio_button.setChecked(True)

    def update_smoothing_settings(self) -> None:
        """Updates global smoothing settings."""
        conductance: str = self.conductance_parameter_input.displayText()
        try:
            global_vars.CONDUCTANCE_PARAMETER = float(conductance)
        except ValueError:
            if user_settings.DEBUG:
                print("Conductance must be a float!")
        self.conductance_parameter_input.setText(str(global_vars.CONDUCTANCE_PARAMETER))
        self.conductance_parameter_input.setPlaceholderText(
            str(global_vars.CONDUCTANCE_PARAMETER)
        )
        global_vars.SMOOTHING_FILTER.SetConductanceParameter(
            global_vars.CONDUCTANCE_PARAMETER
        )

        iterations: str = self.smoothing_iterations_input.displayText()
        try:
            global_vars.SMOOTHING_ITERATIONS = int(iterations)
        except ValueError:
            if user_settings.DEBUG:
                print("Iterations must be an integer!")
        self.smoothing_iterations_input.setText(str(global_vars.SMOOTHING_ITERATIONS))
        self.smoothing_iterations_input.setPlaceholderText(
            str(global_vars.SMOOTHING_ITERATIONS)
        )
        global_vars.SMOOTHING_FILTER.SetNumberOfIterations(
            global_vars.SMOOTHING_ITERATIONS
        )

        time_step: str = self.time_step_input.displayText()
        try:
            global_vars.TIME_STEP = float(time_step)
        except ValueError:
            if user_settings.DEBUG:
                print("Time step must be a float!")
        self.time_step_input.setText(str(global_vars.TIME_STEP))
        self.time_step_input.setPlaceholderText(str(global_vars.TIME_STEP))
        global_vars.SMOOTHING_FILTER.SetTimeStep(global_vars.TIME_STEP)

    def update_binary_filter_settings(self) -> None:
        """Updates global binary filter settings."""
        lower_threshold: str = self.lower_threshold_input.displayText()
        try:
            global_vars.LOWER_THRESHOLD = float(lower_threshold)
        except ValueError:
            pass
        self.lower_threshold_input.setText(str(global_vars.LOWER_THRESHOLD))
        self.lower_threshold_input.setPlaceholderText(str(global_vars.LOWER_THRESHOLD))
        global_vars.BINARY_THRESHOLD_FILTER.SetLowerThreshold(
            global_vars.LOWER_THRESHOLD
        )

        upper_threshold: str = self.upper_threshold_input.displayText()
        try:
            global_vars.UPPER_THRESHOLD = float(upper_threshold)
        except ValueError:
            pass
        self.upper_threshold_input.setText(str(global_vars.UPPER_THRESHOLD))
        self.upper_threshold_input.setPlaceholderText(str(global_vars.UPPER_THRESHOLD))
        global_vars.BINARY_THRESHOLD_FILTER.SetUpperThreshold(
            global_vars.UPPER_THRESHOLD
        )

    def render_scaled_qpixmap_from_qimage(self, q_img: QImage) -> None:
        """Convert q_img to QPixmap and set self.image's pixmap to that pixmap scaled to self.image's size.

        Sets UNSCALED_PIXMAP to the unscaled pixmap generated from the q_img.

        :param q_img:
        :type q_img: QImage
        :return None:
        :rtype None:"""
        global UNSCALED_QPIXMAP
        UNSCALED_QPIXMAP = QPixmap(q_img)
        self.image.setPixmap(
            UNSCALED_QPIXMAP.scaled(
                self.image.size(),
                aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                transformMode=Qt.TransformationMode.SmoothTransformation,
            )
        )

    def resizeEvent(self, event) -> None:
        """This method is called every time the window is resized. Overrides PyQt6's resizeEvent.

        Sets pixmap to UNSCALED_QPIXMAP scaled to self.image's size."""
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

        DOES NOT set text for `image_num_label` and file path labels.

        If `not SETTINGS_VIEW_ENABLED`, also calls `imgproc.contour()` and outlines
        the contour of the QImage (mutating it).

        Additionally, also returns a view of the binary contoured slice if `not SETTINGS_VIEW_ENABLED`.
        This saves work when computing circumference.

        :return: np.ndarray if `not SETTINGS_VIEW_ENABLED` else None
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
                string_to_QColor(user_settings.CONTOUR_COLOR),
            )

        elif global_vars.VIEW != constants.View.Z:
            z_indicator: np.ndarray = np.zeros(
                (rotated_slice.GetSize()[1], rotated_slice.GetSize()[0])
            )
            z_indicator[get_curr_image_size()[2] - global_vars.SLICE - 1, :] = 1
            mask_QImage(
                q_img,
                np.transpose(z_indicator),
                string_to_QColor(user_settings.CONTOUR_COLOR),
            )

        self.render_scaled_qpixmap_from_qimage(q_img)

        if not SETTINGS_VIEW_ENABLED:
            return rv_dummy_var

    def render_smooth_slice(self) -> None:
        """Renders smooth slice in GUI. Allows user to preview result of smoothing settings."""
        self.update_smoothing_settings()
        # Preview should apply filter only on axial slice
        self.set_view_z()
        smooth_slice: sitk.Image = get_curr_smooth_slice()
        q_img: QImage = sitk_slice_to_qimage(smooth_slice)
        self.render_scaled_qpixmap_from_qimage(q_img)

    def render_threshold(self) -> None:
        """Render filtered image slice on UI."""
        # Preview should apply filter only on axial slice
        self.set_view_z()
        if self.otsu_radio_button.isChecked():
            filter_img: sitk.Image = get_curr_otsu_slice()
        else:
            self.update_binary_filter_settings()
            filter_img: sitk.Image = get_curr_binary_thresholded_slice()
        q_img: QImage = sitk_slice_to_qimage(filter_img)
        self.render_scaled_qpixmap_from_qimage(q_img)

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
        if SETTINGS_VIEW_ENABLED:
            raise Exception("Rendering circumference label when SETTINGS_VIEW_ENABLED")
        units: Union[str, None] = get_curr_physical_units()

        # Euler3D rotation has no effect on spacing (see unit test). This is the correct spacing
        # This is also the same as get_curr_rotated_slice().GetSpacing(), just without index [2]
        spacing: tuple = get_curr_image().GetSpacing()

        if user_settings.DEBUG:
            print(f"Computing circumference, and this is the spacing: {spacing}")

        # TODO
        # binary_contour_slice is the transpose of the rotated_slice
        # Thus, should pass spacing values in the reverse order?
        circumference: float = imgproc.length_of_contour_with_spacing(
            binary_contour_slice, spacing[1], spacing[0]
        )
        # circumference: float = imgproc.length_of_contour(binary_contour_slice)
        self.circumference_label.setText(
            f"Calculated Circumference: {round(circumference, constants.NUM_DIGITS_TO_ROUND_TO)} {units if units is not None else MESSAGE_TO_SHOW_IF_UNITS_NOT_FOUND}"
        )

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

        Also updates rotation and slice num labels."""
        self.x_slider.setValue(global_vars.THETA_X)
        self.y_slider.setValue(global_vars.THETA_Y)
        self.z_slider.setValue(global_vars.THETA_Z)
        self.slice_slider.setMaximum(get_curr_image().GetSize()[View.Z.value] - 1)
        self.slice_slider.setValue(global_vars.SLICE)
        self.x_rotation_label.setText(f"X rotation: {global_vars.THETA_X}°")
        self.y_rotation_label.setText(f"Y rotation: {global_vars.THETA_Y}°")
        self.z_rotation_label.setText(f"Z rotation: {global_vars.THETA_Z}°")
        self.slice_num_label.setText(f"Slice: {global_vars.SLICE}")

    def rotate_x(self):
        """Called when the user updates the x slider.

        Render image and set `x_rotation_label`."""
        x_slider_val: int = self.x_slider.value()
        global_vars.THETA_X = x_slider_val
        self.render_curr_slice()
        self.x_rotation_label.setText(f"X rotation: {x_slider_val}°")

    def rotate_y(self):
        """Called when the user updates the y slider.

        Render image and set `y_rotation_label`."""
        y_slider_val: int = self.y_slider.value()
        global_vars.THETA_Y = y_slider_val
        self.render_curr_slice()
        self.y_rotation_label.setText(f"Y rotation: {y_slider_val}°")

    def rotate_z(self):
        """Called when the user updates the z slider.

        Render image and set `z_rotation_label`."""
        z_slider_val: int = self.z_slider.value()
        global_vars.THETA_Z = z_slider_val
        self.render_curr_slice()
        self.z_rotation_label.setText(f"Z rotation: {z_slider_val}°")

    def slice_update(self):
        """Called when the user updates the slice slider.

        Render image and set `slice_num_label`."""
        slice_slider_val: int = self.slice_slider.value()
        global_vars.SLICE = slice_slider_val
        self.render_curr_slice()
        self.slice_num_label.setText(f"Slice: {slice_slider_val}")

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

    def next_img(self):
        """Called when Next button is clicked.

        Advance index and render."""
        img_helpers.next_img()
        # TODO: This feels inefficient...
        self.orient_curr_image()
        binary_contour_or_none: Union[np.ndarray, None] = self.render_curr_slice()
        self.render_image_num_and_path()

        if not SETTINGS_VIEW_ENABLED:
            # Ignore the type annotation warning. binary_contour_or_none must be binary_contour since not SETTINGS_VIEW_ENABLED
            self.render_circumference(binary_contour_or_none)

    def previous_img(self):
        """Called when Previous button is clicked.

        Decrement index and render."""
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

        Removes current image from `IMAGE_DICT`. Since `IMAGE_DICT` is a reference to an image dict
        in `IMAGE_GROUPS`, it's removed from `IMAGE_GROUPS` as well.

        :returns: None"""
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

        Assume that anything you put here will be overwritten freely."""
        self.image.setPixmap(QPixmap(f":/{user_settings.THEME_NAME}/help.svg"))
        self.image.setStatusTip(
            "This is intentional, if it's a question mark then that's good :), means we can display icons"
        )

    # TODO: File name should also include circumference when not SETTINGS_VIEW_ENABLED?
    def export_curr_slice_as_img(self, extension: str):
        """Called when an Export as image menu item is clicked.

        Exports `self.image` to `settings.OUTPUT_DIR/img/`. Thus, calling this when `SETTINGS_VIEW_ENABLED` will
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
            constants.IMG_DIR
            / f"{file_name}_{'contoured_' if not SETTINGS_VIEW_ENABLED else ''}{global_vars.THETA_X}_{global_vars.THETA_Y}_{global_vars.THETA_Z}_{global_vars.SLICE}.{extension}"
        )
        self.image.pixmap().save(path, extension)

    def orient_curr_image(self) -> None:
        """Orient the current image for the current view (global_vars.VIEW) by applying ORIENT_FILTER on it.

        This mutates the image."""
        img_helpers.orient_curr_image(global_vars.VIEW)


def error_message_box(message: str) -> None:
    """Creates a message box with an error message and red warning icon.

    :param message: the error message to be displayed
    :type message: str
    :return: None
    :rtype: None"""
    ErrorMessageBox(message).exec()


def information_dialog(title: str, message: str) -> None:
    """Create an informational dialog QDialog window with title and message.

    :param title:
    :type title: str
    :param message:
    :type message: str
    :return: None
    :rtype: None"""
    InformationDialog(title, message).exec()


# TODO: Broken
def display_metadata() -> None:
    """Display metadata in window or terminal. Internally, uses sitk.GetMetaData, which doesn't return
    all metadata (e.g., doesn't return spacing values whereas sitk.GetSpacing does).

    Typically, this returns less metadata for NRRD than for NIfTI."""
    if not len(global_vars.IMAGE_DICT):
        print("Can't print metadata when there's no image!")
        return
    message: str = pprint.pformat(get_curr_metadata())
    if user_settings.DISPLAY_ADVANCED_MENU_MESSAGES_IN_TERMINAL:
        print(message)
    else:
        information_dialog("Metadata", message)


def display_dimensions() -> None:
    """Display current image's dimensions in window or terminal."""
    if not len(global_vars.IMAGE_DICT):
        print("Can't print dimensions when there's no image!")
        return
    message: str = pprint.pformat(get_curr_image().GetSize())
    if user_settings.DISPLAY_ADVANCED_MENU_MESSAGES_IN_TERMINAL:
        print(message)
    else:
        information_dialog("Dimensions", message)


# TODO: If updating img_helpers.get_properties(), this needs to be slightly adjusted!
def display_properties() -> None:
    """Display properties in window or terminal.

    Internally, the properties tuple is a tuple of values only and doesn't contain
    field names. This function creates a dictionary with field names for printing. But the dictionary
    doesn't exist in the program."""
    if not len(global_vars.IMAGE_DICT):
        print("No loaded image!")
        return
    curr_properties: tuple = get_curr_properties_tuple()
    fields: tuple = ("center of rotation", "dimensions", "spacing")
    if len(fields) != len(curr_properties):
        print(
            "Update src/GUI/main.print_properties() !\nNumber of fields and number of properties don't match."
        )
        exit(1)
    # Pretty sure the dict(zip(...)) goes through fields in alphabetical order
    message: str = pprint.pformat(dict(zip(fields, curr_properties)))
    if user_settings.DISPLAY_ADVANCED_MENU_MESSAGES_IN_TERMINAL:
        print(message)
    else:
        information_dialog("Properties", message)


def display_direction() -> None:
    """Display current image's direction in window or terminal."""
    if not len(global_vars.IMAGE_DICT):
        print("Can't print direction when there's no image!")
        return
    message: str = pprint.pformat(get_curr_image().GetDirection())
    if user_settings.DISPLAY_ADVANCED_MENU_MESSAGES_IN_TERMINAL:
        print(message)
    else:
        information_dialog("Direction", message)


def display_spacing() -> None:
    """Display current image's spacing in window or terminal."""
    if not len(global_vars.IMAGE_DICT):
        print("Can't print spacing when there's no image!")
        return
    message: str = pprint.pformat(get_curr_image().GetSpacing())
    if user_settings.DISPLAY_ADVANCED_MENU_MESSAGES_IN_TERMINAL:
        print(message)
    else:
        information_dialog("Spacing", message)


def main() -> None:
    """Main entrypoint of GUI."""
    # This import can't go at the top of the file
    # because gui.py.parse_gui_cli() has to set THEME_NAME before the import occurs
    # This imports globally
    # For example, src/GUI/helpers.py can access resource files without having to import there
    importlib.import_module(f"src.GUI.themes.{user_settings.THEME_NAME}.resources")

    app = QApplication(sys.argv)

    # On macOS, sets the application logo in the dock (but no window icon on macOS)
    # TODO
    # On Windows, sets the window icon at the top left of the window (but no dock icon on Windows)
    app.setWindowIcon(QIcon(str(PATH_TO_HCT_LOGO)))

    # TODO: Put arrow buttons on the left and right endpoints of the sliders
    # These arrow buttons already show up if commenting in app.setStyle("Fusion")
    # And commenting out with open stylesheet and app.setStyleSheet
    # We should figure out how to get arrow buttons on sliders for (+, -) 1 precise adjustments.
    # Currently, the sliders allow this (left click on the left or right end), but the arrow buttons
    # are not in the GUI.
    # app.setStyle("Fusion")

    with open(
        constants.THEME_DIR / user_settings.THEME_NAME / f"stylesheet.qss", "r"
    ) as f:
        app.setStyleSheet(f.read())

    MAIN_WINDOW = MainWindow()

    # Non-zero min width and height is needed to prevent
    # this bug https://github.com/COMP523TeamD/HeadCircumferenceTool/issues/42
    # However, this also seems to affect startup GUI size or at least GUI element spacing
    MAIN_WINDOW.setMinimumSize(QSize(1, 1))
    MAIN_WINDOW.resize(
        int(
            user_settings.STARTUP_WIDTH_RATIO * constants.PRIMARY_MONITOR_DIMENSIONS[0]
        ),
        int(
            user_settings.STARTUP_HEIGHT_RATIO * constants.PRIMARY_MONITOR_DIMENSIONS[1]
        ),
    )

    try:
        sys.exit(app.exec())
    except:
        if user_settings.DEBUG:
            print("Exiting")


if __name__ == "__main__":
    import src.utils.parser as parser

    parser.parse_config_json()
    parser.parse_gui_cli()
    main()

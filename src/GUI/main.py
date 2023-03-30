"""Defines MainWindow and main(), the entrypoint of the GUI.

Loads `src/GUI/main.ui`, made in QtDesigner.

Loads `.qss` stylesheets and `resources.py` (icons) files, generated
by BreezeStyleSheets. Our fork of the repo: https://github.com/COMP523TeamD/BreezeStyleSheets.

Native menu bar (macOS) is enabled since we are now using only one window.
See https://github.com/COMP523TeamD/HeadCircumferenceTool/issues/9."""

import importlib
import sys
import webbrowser
from pathlib import Path
from typing import Union

import SimpleITK as sitk
import numpy as np
from PyQt6 import QtWidgets
from PyQt6 import QtGui
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt6.uic.load_ui import loadUi

# qimage2ndarray needs to go after PyQt6 imports or there will be a ModuleNotFoundError.
import qimage2ndarray
import pprint

# The regular Python 3.7+ dict maintains insertion order.
# This is used only in print_properties()
from collections import OrderedDict

import src.utils.constants as constants

# Note, do not use imports like
# from src.utils.global_vars import IMAGE_DICT
# This would make the global variables not work
import src.utils.global_vars as global_vars
import src.utils.imgproc as imgproc
import src.utils.user_settings as settings
from src.GUI.helpers import (
    string_to_QColor,
    mask_QImage,
)

from src.utils.img_helpers import (
    initialize_globals,
    update_image_groups,
    curr_image,
    curr_rotated_slice,
    curr_metadata,
    curr_physical_units,
    curr_path,
    get_curr_properties_tuple,
    get_middle_of_z_dimension,
    get_curr_spacing,
)

import src.utils.img_helpers as img_helpers

PATH_TO_UI_FILE: Path = Path("src") / "GUI" / "main.ui"
PATH_TO_HCT_LOGO: Path = Path("src") / "GUI" / "static" / "hct_logo.png"
DEFAULT_CIRCUMFERENCE_LABEL_TEXT: str = "Calculated Circumference: N/A"
DEFAULT_IMAGE_PATH_LABEL_TEXT: str = "Image path"
GITHUB_LINK: str = "https://github.com/COMP523TeamD/HeadCircumferenceTool"
DOCUMENTATION_LINK: str = "https://headcircumferencetool.readthedocs.io/en/latest/"
DEFAULT_IMAGE_TEXT: str = "Select images using File > Open!"
DEFAULT_IMAGE_NUM_LABEL_TEXT: str = "Image 0 of 0"
DEFAULT_IMAGE_STATUS_TEXT: str = "Image path is displayed here."
# TODO: Do we assume units are mm unless specified otherwise?
MESSAGE_TO_SHOW_IF_UNITS_NOT_FOUND: str = "units not found"


class MainWindow(QMainWindow):
    """Main window of the application.

    Settings mode and circumference mode."""

    def __init__(self):
        """Load main.ui file and connect GUI events to methods/functions.

        Sets window title and icon."""
        super(MainWindow, self).__init__()
        loadUi(str(PATH_TO_UI_FILE), self)
        self.setWindowTitle("Head Circumference Tool")
        self.setWindowIcon(QtGui.QIcon(str(PATH_TO_HCT_LOGO)))
        self.action_open.triggered.connect(lambda: self.browse_files(False))
        self.action_add_images.triggered.connect(lambda: self.browse_files(True))
        self.action_remove_image.triggered.connect(self.remove_curr_img)
        self.action_exit.triggered.connect(exit)
        self.action_github.triggered.connect(lambda: webbrowser.open(GITHUB_LINK))
        self.action_documentation.triggered.connect(
            lambda: webbrowser.open(DOCUMENTATION_LINK)
        )
        self.action_test_show_resource.triggered.connect(self.test_show_resource)
        self.action_print_metadata.triggered.connect(print_metadata)
        self.action_print_dimensions.triggered.connect(print_dimensions)
        self.action_print_properties.triggered.connect(print_properties)
        self.action_print_spacing.triggered.connect(print_spacing)
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
        self.show()

    def render_initial_view(self) -> None:
        """Called after File > Open. Enables GUI elements."""
        self.action_open.setEnabled(True)
        self.action_add_images.setEnabled(True)
        self.action_remove_image.setEnabled(True)
        self.image.setEnabled(True)
        self.image_path_label.setEnabled(True)
        self.image_num_label.setEnabled(True)
        self.previous_button.setEnabled(True)
        self.next_button.setEnabled(True)
        self.apply_button.setEnabled(True)
        self.x_slider.setEnabled(True)
        self.y_slider.setEnabled(True)
        self.z_slider.setEnabled(True)
        self.slice_slider.setEnabled(True)
        self.x_rotation_label.setEnabled(True)
        self.y_rotation_label.setEnabled(True)
        self.z_rotation_label.setEnabled(True)
        self.slice_num_label.setEnabled(True)
        self.reset_button.setEnabled(True)
        self.smoothing_preview_button.setEnabled(True)
        self.otsu_radio_button.setEnabled(True)
        self.binary_radio_button.setEnabled(True)
        self.threshold_preview_button.setEnabled(True)
        self.action_export_csv.setEnabled(False)
        self.action_export_png.setEnabled(True)
        self.action_export_jpg.setEnabled(True)
        self.action_export_bmp.setEnabled(True)
        self.action_export_ppm.setEnabled(True)
        self.action_export_xbm.setEnabled(True)
        self.action_export_xpm.setEnabled(True)

    def settings_export_view_toggle(self) -> None:
        """Called when clicking Apply (in settings mode) or Adjust (in circumference mode).

        Toggle SETTINGS_VIEW_ENABLED, change apply button text, render stuff depending on the current mode.

        Enables/disables GUI elements depending on the value of SETTINGS_VIEW_ENABLED.
        """
        global_vars.SETTINGS_VIEW_ENABLED = not global_vars.SETTINGS_VIEW_ENABLED
        settings_view_enabled = global_vars.SETTINGS_VIEW_ENABLED
        if settings_view_enabled:
            self.apply_button.setText("Apply")
            self.circumference_label.setText(DEFAULT_CIRCUMFERENCE_LABEL_TEXT)
            # Render uncontoured slice after pressing adjust
            self.render_curr_slice()
        else:
            self.apply_button.setText("Adjust")
            # Ignore the type annotation error here.
            # render_curr_slice() must return np.ndarray since not settings_view_enabled here
            binary_contour_slice: np.ndarray = self.render_curr_slice()
            self.render_circumference(binary_contour_slice)

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
        self.threshold_preview_button.setEnabled(settings_view_enabled)
        self.action_export_csv.setEnabled(not settings_view_enabled)
        self.circumference_label.setEnabled(not settings_view_enabled)
        self.export_button.setEnabled(not settings_view_enabled)

    # TODO: Could just construct a new MainWindow()? Maybe might not work?
    def disable_elements(self) -> None:
        """Called when the list is now empty, i.e. just removed from list of length 1."""
        self.action_open.setEnabled(True)
        self.action_add_images.setEnabled(False)
        self.action_remove_image.setEnabled(False)
        self.circumference_label.setEnabled(False)
        self.circumference_label.setText(DEFAULT_CIRCUMFERENCE_LABEL_TEXT)
        # Keep this enabled to show the text "Select images..." without it being transparent
        self.image.setEnabled(True)
        self.image.clear()
        self.image.setText(DEFAULT_IMAGE_TEXT)
        self.image.setStatusTip(DEFAULT_IMAGE_STATUS_TEXT)
        self.image_path_label.setEnabled(False)
        self.image_path_label.setText(DEFAULT_IMAGE_PATH_LABEL_TEXT)
        self.image_num_label.setEnabled(False)
        self.image_num_label.setText(DEFAULT_IMAGE_NUM_LABEL_TEXT)
        self.previous_button.setEnabled(False)
        self.next_button.setEnabled(False)
        self.apply_button.setEnabled(False)
        self.apply_button.setText("Apply")
        self.x_slider.setEnabled(False)
        self.y_slider.setEnabled(False)
        self.z_slider.setEnabled(False)
        self.slice_slider.setEnabled(False)
        self.reset_button.setEnabled(False)
        self.action_export_csv.setEnabled(False)
        self.action_export_png.setEnabled(False)
        self.action_export_jpg.setEnabled(False)
        self.action_export_bmp.setEnabled(False)
        self.action_export_ppm.setEnabled(False)
        self.action_export_xbm.setEnabled(False)
        self.action_export_xpm.setEnabled(False)
        self.x_rotation_label.setEnabled(False)
        self.y_rotation_label.setEnabled(False)
        self.z_rotation_label.setEnabled(False)
        self.slice_num_label.setEnabled(False)
        self.circumference_label.setEnabled(False)
        self.export_button.setEnabled(False)
        self.smoothing_preview_button.setEnabled(False)
        self.otsu_radio_button.setEnabled(False)
        self.binary_radio_button.setEnabled(False)
        self.threshold_preview_button.setEnabled(False)

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
            self, "Open files", str(settings.FILE_BROWSER_START_DIR), file_filter
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
            self.render_initial_view()
            self.render_image_num_and_path()
            self.render_curr_slice()
        else:
            # Doesn't need to re-render sliders to set max value of slice slider.
            # update_image_groups does not change the batch.
            # Therefore, max value of slice slider does not change.
            # Must render image_num.
            # Does not need to render current slice. Images are added to the end of the dict.
            # And adding duplicate key doesn't change key order.
            update_image_groups(path_list)
            self.render_image_num_and_path()

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
        rotated_slice: sitk.Image = curr_rotated_slice()

        slice_np: np.ndarray = sitk.GetArrayFromImage(rotated_slice)

        q_img = qimage2ndarray.array2qimage(slice_np, normalize=True)

        rv_dummy_var: np.ndarray = np.zeros(0)

        if not global_vars.SETTINGS_VIEW_ENABLED:
            binary_contour_slice: np.ndarray = imgproc.contour(rotated_slice, False)
            rv_dummy_var = binary_contour_slice
            mask_QImage(
                q_img,
                np.transpose(binary_contour_slice),
                string_to_QColor(settings.CONTOUR_COLOR),
            )

        q_pixmap: QPixmap = QPixmap(q_img)

        self.image.setPixmap(q_pixmap)

        if not global_vars.SETTINGS_VIEW_ENABLED:
            return rv_dummy_var

    def render_circumference(self, binary_contour_slice: np.ndarray) -> None:
        """Called after pressing Apply or when
        not SETTINGS_VIEW_ENABLED and (pressing Next or Previous or Remove Image)

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
        units: Union[str, None] = curr_physical_units()
        circumference: float = imgproc.length_of_contour(binary_contour_slice)
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
        self.image_path_label.setText(str(curr_path().name))
        self.image_path_label.setStatusTip(str(curr_path()))
        self.image.setStatusTip(str(curr_path()))

    def render_all_sliders(self) -> None:
        """Sets all slider values to the global rotation and slice values.
        Also updates maximum value of slice slider.

        Called on reset. Will need to be called when updating batch index, if we implement this.

        Not called when the user updates a slider.

        Also updates rotation and slice num labels."""
        self.x_slider.setValue(global_vars.THETA_X)
        self.y_slider.setValue(global_vars.THETA_Y)
        self.z_slider.setValue(global_vars.THETA_Z)
        self.slice_slider.setMaximum(curr_image().GetSize()[2] - 1)
        self.slice_slider.setValue(global_vars.SLICE)
        self.x_rotation_label.setText(f"X rotation: {global_vars.THETA_X}°")
        self.y_rotation_label.setText(f"Y rotation: {global_vars.THETA_Y}°")
        self.z_rotation_label.setText(f"Z rotation: {global_vars.THETA_Z}°")
        self.slice_num_label.setText(f"Slice: {global_vars.SLICE}")

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
        binary_contour_or_none: Union[np.ndarray, None] = self.render_curr_slice()
        self.render_image_num_and_path()

        if not global_vars.SETTINGS_VIEW_ENABLED:
            # Ignore the type annotation error. binary_contour_or_none must be binary_contour since not SETTINGS_VIEW_ENABLED
            self.render_circumference(binary_contour_or_none)

    def previous_img(self):
        """Called when Previous button is clicked.

        Decrement index and render."""
        img_helpers.previous_img()
        binary_contour_or_none: Union[np.ndarray, None] = self.render_curr_slice()
        self.render_image_num_and_path()

        if not global_vars.SETTINGS_VIEW_ENABLED:
            # Ignore the type annotation error. binary_contour_or_none must be binary_contour since not SETTINGS_VIEW_ENABLED
            self.render_circumference(binary_contour_or_none)

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
        global_vars.SLICE = get_middle_of_z_dimension(curr_image())
        self.render_curr_slice()
        self.render_all_sliders()

    def test_show_resource(self) -> None:
        """Connected to Test > Test show resource. Dummy function for testing stuff.

        Currently displays `help.svg` (`help.svg` not in the repo since it's compiled in resources.py).
        """
        self.image.setPixmap(QPixmap(f":/{settings.THEME_NAME}/help.svg"))
        self.image.setStatusTip(
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
            if settings.EXPORTED_FILE_NAMES_USE_INDEX
            else curr_path().name
        )
        path: str = str(
            settings.IMG_DIR
            / f"{file_name}_{'contoured_' if not global_vars.SETTINGS_VIEW_ENABLED else ''}{global_vars.THETA_X}_{global_vars.THETA_Y}_{global_vars.THETA_Z}_{global_vars.SLICE}.{extension}"
        )
        self.image.pixmap().save(path, extension)


def print_metadata() -> None:
    """Print current image's metadata to terminal. Internally, uses sitk.GetMetaData, which doesn't return
    all metadata (e.g., doesn't return spacing values whereas sitk.GetSpacing does).

    Typically, this returns less metdata for NRRD than for NIfTI."""

    if not len(global_vars.IMAGE_DICT):
        print("Can't print metadata when there's no image!")
        return
    pprint.pprint(curr_metadata())


def print_dimensions() -> None:
    """Print currently displayed image's dimensions to terminal."""
    if not len(global_vars.IMAGE_DICT):
        print("Can't print dimensions when there's no image!")
        return
    print(curr_image().GetSize())


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


# Spacing doesn't change when the image rotates.
def print_spacing() -> None:
    """Print current image's spacing to terminal."""
    print(get_curr_spacing())


def main() -> None:
    """Main entrypoint of GUI."""
    # This import can't go at the top of the file
    # because gui.py.parse_gui_cli() has to set THEME_NAME before the import occurs
    importlib.import_module(f"src.GUI.themes.{settings.THEME_NAME}.resources")

    if not settings.IMG_DIR.exists():
        settings.IMG_DIR.mkdir()

    app = QApplication(sys.argv)

    # TODO: This puts arrow buttons on the left and right endpoints of the sliders
    # If the QSS below isn't loaded (i.e., comment out the below two lines)
    # We should figure out how to get arrow buttons on sliders for (+, -) 1 precise adjustments.
    # Currently, the sliders allow this (left click on the left or right end), but it's not obvious in the GUI.

    # app.setStyle('Fusion')

    with open(constants.THEME_DIR / settings.THEME_NAME / f"stylesheet.qss", "r") as f:
        app.setStyleSheet(f.read())

    MAIN_WINDOW = MainWindow()
    MAIN_WINDOW.setMinimumWidth(
        int(settings.MIN_WIDTH_RATIO * settings.PRIMARY_MONITOR_DIMENSIONS[0])
    )
    MAIN_WINDOW.setMinimumHeight(
        int(settings.MIN_HEIGHT_RATIO * settings.PRIMARY_MONITOR_DIMENSIONS[1])
    )

    MAIN_WINDOW.setMaximumWidth(
        int(settings.MAX_WIDTH_RATIO * settings.PRIMARY_MONITOR_DIMENSIONS[0])
    )
    MAIN_WINDOW.setMaximumHeight(
        int(settings.MAX_HEIGHT_RATIO * settings.PRIMARY_MONITOR_DIMENSIONS[1])
    )

    try:
        sys.exit(app.exec())
    except:
        if settings.DEBUG:
            print("Exiting")


if __name__ == "__main__":
    import src.utils.parser as parser
    parser.parse_json()
    parser.parse_gui_cli()
    main()

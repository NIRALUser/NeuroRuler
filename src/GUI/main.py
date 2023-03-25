"""Defines MainWindow and CircumferenceWindow and main(), the entrypoint of the GUI.

Loads `src/GUI/main.ui` and `src/GUI/circumference.ui`, both made in QtDesigner.

In addition, also loads `.qss` stylesheets and `resources.py` (icons) files, generated
by BreezeStyleSheets. Our fork of the repo is here: https://github.com/COMP523TeamD/BreezeStyleSheets.

There's a lot of boilerplate here to get current slice, i.e. `global_vars.IMAGE_DICT[global_vars.IMAGE_DICT.index]`
Isn't too inefficient but could be improved. Tried more global variables but it was pretty bad.

`MainWindow` and `CircumferenceWindow` are in the same file due to the need for shared global variables.

Functions like `render_curr_slice` and `export_curr_slice_as_img` that are common to both windows
are made functions instead of methods to avoid duplicated code. They do behave slightly differently
depending on the window, so the currently active window is computed in these functions.

If a behavior is unique to a window, then it is a method in the class (though it could be made a function).

Native menu bar is currently disabled. See https://github.com/COMP523TeamD/HeadCircumferenceTool/issues/9.
tl;dr on macOS, there can only be one menubar shared between the two classes. Now that we want only one window,
we can easily have a native menu bar (just check native menu bar checkbox in QtDesigner)."""

import importlib
import sys
import webbrowser
from pathlib import Path
from typing import Union

import SimpleITK as sitk
import numpy as np
from PyQt6 import QtWidgets
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt6.uic.load_ui import loadUi

# qimage2ndarray needs to go after PyQt6 imports or there will be a ModuleNotFoundError.
import qimage2ndarray
import pprint

import src.utils.constants as constants

# Note, do not use imports like
# from src.utils.global_vars import IMAGE_DICT.
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
)
import src.utils.img_helpers as img_helpers

from src.utils.parse_cli import parse_gui_cli

DEFAULT_CIRCUMFERENCE_LABEL_TEXT: str = "Calculated Circumference: N/A"
DEFAULT_IMAGE_PATH_LABEL_TEXT: str = "Image path"
GITHUB_LINK: str = "https://github.com/COMP523TeamD/HeadCircumferenceTool"
DOCUMENTATION_LINK: str = "https://headcircumferencetool.readthedocs.io/en/latest/"
DEFAULT_IMAGE_TEXT: str = "Select images using File > Open!"
DEFAULT_IMAGE_NUM_LABEL_TEXT: str = "Image 0 of 0"
DEFAULT_IMAGE_STATUS_TEXT: str = "Image path is displayed here."
MESSAGE_TO_SHOW_IF_UNITS_NOT_FOUND: str = "units not found in metadata"


class MainWindow(QMainWindow):
    """Main window of the application.

    Displays image and rotation & slice sliders, along with a reset button.

    Also displays the index of the current image and previous & next buttons."""

    def __init__(self):
        """Load main.ui file from QtDesigner and connect GUI events to methods/functions."""
        super(MainWindow, self).__init__()
        loadUi(str(Path("src") / "GUI" / "main.ui"), self)
        self.setWindowTitle("Head Circumference Tool")
        self._enabled = False
        """Set to True on first call to enable_elements."""
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
        self.action_print_curr_properties_tuple.triggered.connect(
            print_curr_properties_tuple
        )
        self.action_export_png.triggered.connect(
            lambda: export_curr_slice_as_img("png")
        )
        self.action_export_jpg.triggered.connect(
            lambda: export_curr_slice_as_img("jpg")
        )
        self.action_export_bmp.triggered.connect(
            lambda: export_curr_slice_as_img("bmp")
        )
        self.action_export_ppm.triggered.connect(
            lambda: export_curr_slice_as_img("ppm")
        )
        self.action_export_xbm.triggered.connect(
            lambda: export_curr_slice_as_img("xbm")
        )
        self.action_export_xpm.triggered.connect(
            lambda: export_curr_slice_as_img("xpm")
        )
        self.next_button.clicked.connect(self.next_img)
        self.previous_button.clicked.connect(self.previous_img)
        self.apply_button.clicked.connect(goto_circumference)
        self.x_slider.valueChanged.connect(self.rotate_x)
        self.y_slider.valueChanged.connect(self.rotate_y)
        self.z_slider.valueChanged.connect(self.rotate_z)
        self.slice_slider.valueChanged.connect(self.slice_update)
        self.reset_button.clicked.connect(self.reset_settings)
        self.show()

    def enable_elements(self) -> None:
        """Called when File > Open is clicked and when switching from CircumferenceWindow to MainWindow
        (i.e., when Adjust button is clicked).

        Enable image, menu items, buttons, and sliders. Disable Export > CSV."""
        self._enabled = True
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
        self.reset_button.setEnabled(True)
        self.action_export_csv.setEnabled(False)
        self.action_export_png.setEnabled(True)
        self.action_export_jpg.setEnabled(True)
        self.action_export_bmp.setEnabled(True)
        self.action_export_ppm.setEnabled(True)
        self.action_export_xbm.setEnabled(True)
        self.action_export_xpm.setEnabled(True)
        self.x_rotation_label.setEnabled(True)
        self.y_rotation_label.setEnabled(True)
        self.z_rotation_label.setEnabled(True)
        self.slice_num_label.setEnabled(True)
        self.smoothing_preview_button.setEnabled(True)
        self.otsu_radio_button.setEnabled(True)
        self.binary_radio_button.setEnabled(True)
        self.threshold_preview_button.setEnabled(True)

    # TODO: Could just construct a new MainWindow()? Maybe might not work?
    def disable_elements(self) -> None:
        """Called when the list is now empty, i.e. just removed from list of length 1.

        Needs only handle the items that will be different from the usual state."""
        # self.action_open.setEnabled(True)
        self.action_add_images.setEnabled(False)
        self.action_remove_image.setEnabled(False)
        self.circumference_label.setEnabled(False)
        self.circumference_label.setText(DEFAULT_CIRCUMFERENCE_LABEL_TEXT)
        self.image.setEnabled(False)
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
        self.x_slider.setEnabled(False)
        self.y_slider.setEnabled(False)
        self.z_slider.setEnabled(False)
        self.slice_slider.setEnabled(False)
        self.reset_button.setEnabled(False)
        # self.action_export_csv.setEnabled(False)
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

    def render_all_sliders(self) -> None:
        """Sets all slider values to the global rotation and slice values.

        Called on reset.

        Not called when the user updates a slider.

        Also updates rotation and slice num labels."""
        self.x_slider.setValue(global_vars.THETA_X)
        self.y_slider.setValue(global_vars.THETA_Y)
        self.z_slider.setValue(global_vars.THETA_Z)
        # Probably not necessary. Just in case.
        self.slice_slider.setMaximum(curr_image().GetSize()[2] - 1)
        self.slice_slider.setValue(global_vars.SLICE)
        self.x_rotation_label.setText(f"X rotation: {global_vars.THETA_X}°")
        self.y_rotation_label.setText(f"Y rotation: {global_vars.THETA_Y}°")
        self.z_rotation_label.setText(f"Z rotation: {global_vars.THETA_Z}°")
        self.slice_num_label.setText(f"Slice: {global_vars.SLICE}")

    def browse_files(self, extend: bool) -> None:
        """Called after File > Open or File > Add Images.

        If `extend`, then `IMAGE_GROUPS` will be extended with new files. Else, `IMAGE_GROUPS` will be cleared and
        (re)initialized (e.g. when choosing files for the first time or just re-opening).

        Since IMAGE_DICT is a reference to the first image dict in IMAGE_GROUPS, IMAGE_DICT is also cleared and
        (re)initialized, by extension.

        Opens file menu and calls `enable_and_disable_elements()` if not `extend`.

        Lastly, calls `render_curr_slice()` or `refresh()`.

        :param extend: Whether to clear IMAGE_GROUPS and (re)initialize or extend on it
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
            self.enable_elements()
        else:
            update_image_groups(path_list)

        render_curr_slice()

    # TODO: Due to the images now being a dict, we can easily let the user remove a range of images if they want
    def remove_curr_img(self) -> None:
        """Called after File > Remove File.

        Removes current image from `IMAGE_DICT`.

        :returns: None"""
        img_helpers.del_curr_img()

        if len(global_vars.IMAGE_DICT) == 0:
            self.disable_elements()
            return

        render_curr_slice()

    def next_img(self):
        """Called when Next button is clicked.

        Advance index and refresh."""
        img_helpers.next_img()
        render_curr_slice()

    def previous_img(self):
        """Called when Previous button is clicked.

        Decrement index and refresh."""
        img_helpers.previous_img()
        render_curr_slice()

    def rotate_x(self):
        """Called any time the user updates the x slider.

        Render image and set `x_rotation_label`."""
        x_slider_val: int = self.x_slider.value()
        global_vars.THETA_X = x_slider_val
        render_curr_slice()
        self.x_rotation_label.setText(f"X rotation: {x_slider_val}°")

    def rotate_y(self):
        """Called any time the user updates the y slider.

        Render image and set `y_rotation_label`."""
        y_slider_val: int = self.y_slider.value()
        global_vars.THETA_Y = y_slider_val
        render_curr_slice()
        self.y_rotation_label.setText(f"Y rotation: {y_slider_val}°")

    def rotate_z(self):
        """Called any time the user updates the z slider.

        Render image and set `z_rotation_label`."""
        z_slider_val: int = self.z_slider.value()
        global_vars.THETA_Z = z_slider_val
        render_curr_slice()
        self.z_rotation_label.setText(f"Z rotation: {z_slider_val}°")

    def slice_update(self):
        """Called any time the user updates the slice slider.

        Render image and set `slice_num_label`."""
        slice_slider_val: int = self.slice_slider.value()
        global_vars.SLICE = slice_slider_val
        render_curr_slice()
        self.slice_num_label.setText(f"Slice: {slice_slider_val}")

    def reset_settings(self):
        """Called when Reset is clicked.

        Resets rotation values to 0 and slice num to the default `int((z-1)/2)`
        for the current image, then `refresh`es."""
        global_vars.THETA_X = 0
        global_vars.THETA_Y = 0
        global_vars.THETA_Z = 0
        global_vars.SLICE = img_helpers.get_middle_of_z_dimension(curr_image())
        render_curr_slice()
        self.render_all_sliders()

    def test_show_resource(self) -> None:
        """Connected to Test > Test show resource. Dummy function for testing stuff.

        Currently displays `help.svg` (`help.svg` not in the repo since it's compiled in resources.py).
        """
        self.image.setPixmap(QPixmap(f":/{settings.THEME_NAME}/help.svg"))
        self.image.setStatusTip(
            "This is intentional, if it's a question mark then that's good :), means we can display icons"
        )


class CircumferenceWindow(QMainWindow):
    """Displayed after pressing Apply in MainWindow.

    Displays the same MRI slice as in MainWindow previously but overlays contour on top.
    Also displays the computed circumference.

    No sliders (yet) but displays rotation & slice values.
    CircumferenceWindow is NOT finished.

    There should be only one instance of this class."""

    def __init__(self):
        """Load circumference.ui and connect GUI events to methods/functions."""
        super(CircumferenceWindow, self).__init__()
        loadUi(str(Path("src") / "GUI" / "circumference.ui"), self)
        self.enable_and_disable_elements()
        self.action_exit.triggered.connect(exit)
        self.action_github.triggered.connect(lambda: webbrowser.open(GITHUB_LINK))
        self.action_documentation.triggered.connect(
            lambda: webbrowser.open(DOCUMENTATION_LINK)
        )
        self.action_print_metadata.triggered.connect(print_metadata)
        self.action_print_dimensions.triggered.connect(print_dimensions)
        self.action_print_curr_properties_tuple.triggered.connect(
            print_curr_properties_tuple
        )
        self.action_export_png.triggered.connect(
            lambda: export_curr_slice_as_img("png")
        )
        self.action_export_jpg.triggered.connect(
            lambda: export_curr_slice_as_img("jpg")
        )
        self.action_export_bmp.triggered.connect(
            lambda: export_curr_slice_as_img("bmp")
        )
        self.action_export_ppm.triggered.connect(
            lambda: export_curr_slice_as_img("ppm")
        )
        self.action_export_xbm.triggered.connect(
            lambda: export_curr_slice_as_img("xbm")
        )
        self.action_export_xpm.triggered.connect(
            lambda: export_curr_slice_as_img("xpm")
        )
        self.adjust_slice_button.clicked.connect(goto_main)
        self.show()

    def enable_and_disable_elements(self):
        """Called when switching from MainWindow to CircumferenceWindow (i.e., Apply button is clicked).

        Needs only handle the things that are different from MainWindow."""
        self.action_open.setEnabled(False)
        self.action_export_csv.setEnabled(True)


def render_curr_slice() -> Union[np.ndarray, None]:
    """Resamples the currently selected MRIImage using its rotation and slice settings,
    then renders the resulting slice in the GUI.

    Also sets text for `image_num_label` and file path in the status bar tooltip.

    If `curr_window == CIRCUMFERENCE_WINDOW`, also calls `imgproc.contour()` to outline
    the contour of the image. Note `==`, not `isinstance()`, because there should
    be only one global instance of `CircumferenceWindow`.

    Additionally, also returns a view of the binary contoured slice if `curr_window == CIRCUMFERENCE_WINDOW`.
    This saves work in `goto_circumference`.

    NOTE: This function relies on the object names `image` and `image_num_label` being
    the same for `MainWindow` and `CircumferenceWindow` in the `.ui` files.

    :return: np.ndarray if `curr_window == CIRCUMFERENCE_WINDOW` else None
    :rtype: np.ndarray or None"""
    curr_window = STACKED_WIDGET.currentWidget()
    rotated_slice: sitk.Image = curr_rotated_slice()

    slice_np: np.ndarray = sitk.GetArrayFromImage(rotated_slice)

    q_img = qimage2ndarray.array2qimage(slice_np, normalize=True)

    rv_dummy_var: np.ndarray = np.zeros(0)

    if curr_window == CIRCUMFERENCE_WINDOW:
        binary_contour_slice: np.ndarray = imgproc.contour(rotated_slice, False)
        rv_dummy_var = binary_contour_slice
        mask_QImage(
            q_img,
            np.transpose(binary_contour_slice),
            string_to_QColor(settings.CONTOUR_COLOR),
        )

    q_pixmap: QPixmap = QPixmap(q_img)

    curr_window.image.setPixmap(q_pixmap)
    curr_window.image_num_label.setText(
        f"Image {global_vars.CURR_IMAGE_INDEX + 1} of {len(global_vars.IMAGE_DICT)}"
    )
    if curr_window == MAIN_WINDOW:
        curr_window.image_path_label.setText(str(curr_path().name))
        curr_window.image_path_label.setStatusTip(str(curr_path()))
    curr_window.image.setStatusTip(
        str(
            curr_path()
            if settings.IMAGE_STATUS_BAR_SHOWS_FULL_PATH
            else curr_path().name
        )
    )

    if curr_window == CIRCUMFERENCE_WINDOW:
        return rv_dummy_var


def export_curr_slice_as_img(extension: str):
    """Called when an Export as image menu item is clicked.

    Exports `curr_window.image` to `settings.IMG_DIR`. So, calling this in CircumferenceWindow will
    save an image with its contour outlined.

    Filename has format <file_name>_[contoured_]<theta_x>_<theta_y>_<theta_z>_<slice_num>.<extension>

    contoured_ will be in the name if `current_window == CIRCUMFERENCE_WINDOW`.

    Supported formats in this function are the ones supported by QPixmap,
    namely BMP, JPG, JPEG, PNG, PPM, XBM, XPM.

    NOTE: This function relies on the object name `image` being
    the same for `MainWindow` and `CircumferenceWindow` in the `.ui` files.

    :return: `None`"""
    curr_window = STACKED_WIDGET.currentWidget()
    file_name = (
        global_vars.CURR_IMAGE_INDEX + 1
        if settings.EXPORTED_FILE_NAMES_USE_INDEX
        else curr_path().name
    )
    path: str = str(
        settings.IMG_DIR
        / f"{file_name}_{'contoured_' if curr_window == CIRCUMFERENCE_WINDOW else ''}{global_vars.THETA_X}_{global_vars.THETA_Y}_{global_vars.THETA_Z}_{global_vars.SLICE}.{extension}"
    )
    curr_window.image.pixmap().save(path, extension)


def goto_circumference() -> None:
    """Called when MainWindow's Apply button is clicked.

    From MainWindow, switch to CircumferenceWindow.

    Enable and disable CircumferenceWindow GUI elements.

    Compute circumference and update slice settings.

    Re-render contoured MRI slice.

    :return: `None`"""
    STACKED_WIDGET.setCurrentWidget(CIRCUMFERENCE_WINDOW)
    units: Union[str, None] = curr_physical_units()
    CIRCUMFERENCE_WINDOW.enable_and_disable_elements()

    # Ignore the error message. render_curr_slice() always returns np.ndarray here
    # since curr_window must be CIRCUMFERENCE_WINDOW here.

    binary_contour_slice: np.ndarray = render_curr_slice()

    circumference: float = imgproc.length_of_contour(binary_contour_slice)
    CIRCUMFERENCE_WINDOW.circumference_label.setText(
        f"Circumference: {round(circumference, constants.NUM_DIGITS_TO_ROUND_TO)} {units if units is not None else MESSAGE_TO_SHOW_IF_UNITS_NOT_FOUND}"
    )
    CIRCUMFERENCE_WINDOW.slice_settings_text.setText(
        f"X rotation: {global_vars.THETA_X}°\nY rotation: {global_vars.THETA_Y}°\nZ rotation: {global_vars.THETA_Z}°\nSlice: {global_vars.SLICE}"
    )


def print_metadata() -> None:
    """Print current MRIImage's metadata to terminal.

    NRRD files typically don't have a lot of metadata compared to the NIfTI..."""
    if not len(global_vars.IMAGE_DICT):
        print("Can't print metadata when there's no image!")
        return
    pprint.pprint(curr_metadata())


def print_dimensions() -> None:
    """Print current MRIImage's dimensions to terminal."""
    if not len(global_vars.IMAGE_DICT):
        print("Can't print dimensions when there's no image!")
        return
    print(curr_image().GetSize())


def print_curr_properties_tuple() -> None:
    """Print current batch's properties tuple to terminal."""
    print(get_curr_properties_tuple())


def goto_main() -> None:
    """Called when CircumferenceWindow's Adjust button is clicked.

    From CircumferenceWindow, switch to MainWindow.

    Enables and disables MainWindow GUI elements.

    :return: `None`"""
    STACKED_WIDGET.setCurrentWidget(MAIN_WINDOW)
    render_curr_slice()
    MAIN_WINDOW.enable_elements()


def main() -> None:
    """Main entrypoint of GUI."""
    parse_gui_cli()

    # See MainWindow.test for an example of how to access a resource
    # This import can't go at the top because parse_gui_cli has to get THEME_NAME before the import
    importlib.import_module(f"src.GUI.themes.{settings.THEME_NAME}.resources")

    if not settings.IMG_DIR.exists():
        settings.IMG_DIR.mkdir()

    app = QApplication(sys.argv)
    # This puts arrow buttons on the sliders but makes sliding stop early sometimes?
    # app.setStyle('Fusion')

    with open(constants.THEME_DIR / settings.THEME_NAME / f"stylesheet.qss", "r") as f:
        app.setStyleSheet(f.read())

    global STACKED_WIDGET
    global MAIN_WINDOW
    global CIRCUMFERENCE_WINDOW
    # This holds MainWindow and CircumferenceWindow.
    # Setting the index allows for switching between windows.
    STACKED_WIDGET = QtWidgets.QStackedWidget()
    MAIN_WINDOW = MainWindow()
    CIRCUMFERENCE_WINDOW = CircumferenceWindow()

    STACKED_WIDGET.addWidget(MAIN_WINDOW)
    STACKED_WIDGET.addWidget(CIRCUMFERENCE_WINDOW)
    STACKED_WIDGET.setMinimumWidth(settings.MIN_WIDTH)
    STACKED_WIDGET.setMinimumHeight(settings.MIN_HEIGHT)
    STACKED_WIDGET.show()

    try:
        sys.exit(app.exec())
    except:
        if settings.DEBUG:
            print("Exiting")


if __name__ == "__main__":
    main()

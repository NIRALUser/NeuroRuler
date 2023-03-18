"""Entrypoint of GUI stuff.

Loads `src/GUI/main.ui` and `src/GUI/circumference.ui`, both made in QtDesigner.

There's a lot of boilerplate here to get current slice, i.e. `globs.IMAGE_LIST[globs.IMAGE_LIST.index]`

Isn't too inefficient but could be improved. Global variable?

MainWindow and CircumferenceWindow are in the same file due to the need for shared global variables.

Functions like `render_curr_slice` and `export_curr_slice_as_img` that are common to both windows
are made functions instead of methods to avoid duplicated code. They do behave slightly differently
depending on the window, so the currently active window is computed in these functions.

If a behavior is unique to a window, then it is a method in the class (though it could be a function).

Native menu bar is currently disabled. See https://github.com/COMP523TeamD/HeadCircumferenceTool/issues/9.
tl;dr on macOS, there can only be one menubar shared between the two classes. Can work around this by
making MainWindow's QMenuBar global and using that in CircumferenceWindow (i.e., when switching).

Non-native menu bar is a lot simpler but looks worse on macOS."""


import sys
from pathlib import Path
import numpy as np
import SimpleITK as sitk
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QDialog, QApplication, QMainWindow, QFileDialog
from PyQt6.uic.load_ui import loadUi
import qimage2ndarray
import webbrowser
import importlib
from src.utils.mri_image import MRIImage, MRIImageList
import src.utils.imgproc as imgproc
import src.utils.globs as globs
import src.utils.settings as settings
from src.utils.parse_cli import parse_gui_cli

# See MainWindow.test for an example of how to access a resource
# importlib.import_module(f'src.GUI.themes.{settings.THEME_NAME}.resources')

DEFAULT_WIDTH: int = 1000
"""Startup width of the GUI"""
DEFAULT_HEIGHT: int = 700
"""Startup height of the GUI"""
GITHUB_LINK: str = 'https://github.com/COMP523TeamD/HeadCircumferenceTool'
DOCUMENTATION_LINK: str = 'https://headcircumferencetool.readthedocs.io/en/latest/'
DEFAULT_IMAGE_TEXT: str = 'Select images using File > Open!'
DEFAULT_IMAGE_NUM_LABEL_TEXT: str = 'Image 0 of 0'
DEFAULT_IMAGE_STATUS_TEXT: str = 'Image path is displayed here.'


class MainWindow(QMainWindow):
    """Main window of the application.

    Displays image and rotation & slice sliders, along with a reset button.

    Also displays the index of the current image and previous & next buttons."""

    def __init__(self):
        """Load main.ui file from QtDesigner and connect GUI events to methods/functions."""
        super(MainWindow, self).__init__()
        loadUi(str(Path.cwd() / 'src' / 'GUI' / 'main.ui'), self)
        self.setWindowTitle('Head Circumference Tool')
        self.action_open.triggered.connect(lambda: self.browse_files(False))
        self.action_add_images.triggered.connect(
            lambda: self.browse_files(True))
        self.action_remove_image.triggered.connect(self.remove_curr_img)
        self.action_exit.triggered.connect(exit)
        self.action_github.triggered.connect(
            lambda: webbrowser.open(GITHUB_LINK))
        self.action_documentation.triggered.connect(
            lambda: webbrowser.open(DOCUMENTATION_LINK))
        self.action_test.triggered.connect(self.test)
        self.action_export_png.triggered.connect(
            lambda: export_curr_slice_as_img('png'))
        self.action_export_jpg.triggered.connect(
            lambda: export_curr_slice_as_img('jpg'))
        self.action_export_bmp.triggered.connect(
            lambda: export_curr_slice_as_img('bmp'))
        self.action_export_ppm.triggered.connect(
            lambda: export_curr_slice_as_img('ppm'))
        self.action_export_xbm.triggered.connect(
            lambda: export_curr_slice_as_img('xbm'))
        self.action_export_xpm.triggered.connect(
            lambda: export_curr_slice_as_img('xpm'))
        self.next_button.clicked.connect(self.next_img)
        self.previous_button.clicked.connect(self.previous_img)
        self.apply_button.clicked.connect(goto_circumference)
        self.x_slider.valueChanged.connect(self.rotate_x)
        self.y_slider.valueChanged.connect(self.rotate_y)
        self.z_slider.valueChanged.connect(self.rotate_z)
        self.slice_slider.valueChanged.connect(self.slice_update)
        self.reset_button.clicked.connect(self.reset_settings)
        self.show()

    def test(self) -> None:
        """Connected to Test > Test. Dummy function for testing stuff.
        
        Currently displays help.svg (help.svg not in the repo since it's compiled in resources.py)"""
        self.image.setPixmap(QPixmap(f':/{settings.THEME_NAME}/help.svg'))
        self.image.setStatusTip("This is intentional, if it's a question mark then that's good :), means we can display icons")

    def enable_and_disable_elements(self) -> None:
        """Called when File > Open is clicked and when switching from CircumferenceWindow to MainWindow (i.e., when Adjust button is clicked).

        Enable image, menu items, buttons, and sliders."""
        self.action_open.setEnabled(True)
        self.action_remove_image.setEnabled(True)
        self.image.setEnabled(True)
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

    # TODO: Could just construct a new MainWindow()...
    def disable_elements(self) -> None:
        """Called when the list is now empty, i.e. just removed from list of length 1.
        
        Needs only handle the items that will be different from the usual state."""
        # self.action_open.setEnabled(True)
        self.action_remove_image.setEnabled(False)
        self.image.setEnabled(False)
        self.image.clear()
        self.image.setText(DEFAULT_IMAGE_TEXT)
        self.image.setStatusTip(DEFAULT_IMAGE_STATUS_TEXT)
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
        """ Sets all slider values to the values stored in the current `MRIImage`.

        Does not need to be called when the user updates a slider.

        Called on reset and image switch.

        Also updates rotation and slice num labels."""
        curr_mri_image: MRIImage = globs.IMAGE_LIST[globs.IMAGE_LIST.index]
        theta_x = curr_mri_image.theta_x
        theta_y = curr_mri_image.theta_y
        theta_z = curr_mri_image.theta_z
        slice_num = curr_mri_image.slice_z
        self.x_slider.setValue(theta_x)
        self.y_slider.setValue(theta_y)
        self.z_slider.setValue(theta_z)
        self.slice_slider.setMaximum(curr_mri_image.get_size()[2] - 1)
        self.slice_slider.setValue(slice_num)
        self.x_rotation_label.setText(f'X rotation: {theta_x}°')
        self.y_rotation_label.setText(f'Y rotation: {theta_y}°')
        self.z_rotation_label.setText(f'Z rotation: {theta_z}°')
        self.slice_num_label.setText(f'Slice: {slice_num}')

    def browse_files(self, extend: bool) -> None:
        """Called after File > Open or File > Add Images.

        If `extend`, then `IMAGE_LIST` will be extended with new files. Else, `IMAGE_LIST` will be
        initialized (e.g. when choosing files for the first time) and all currently loaded images, if any,
        will be cleared.

        Opens file menu and calls `enable_and_disable_elements()` if not `extend`.

        Lastly, calls `render_curr_slice()` or `refresh()`.

        :return: `None`"""
        file_filter: str = 'MRI images ' + \
            str(globs.SUPPORTED_EXTENSIONS).replace("'", "").replace(",", "")
        # TODO: Let starting directory be a configurable setting in JSON
        # The return value of `getOpenFileNames` is a tuple (list[str], str), where the left element is a list of paths.
        # So `fnames[0][i]` is the i'th path.
        files = QFileDialog.getOpenFileNames(
            self, 'Open files', str(Path.cwd()), file_filter)
        paths = map(Path, files[0])
        images: list[MRIImage] = list(map(MRIImage, paths))

        if extend:
            globs.IMAGE_LIST.extend(images)
            # For setting image_num_label
            render_curr_slice()
        else:
            globs.IMAGE_LIST = MRIImageList(images)
            self.enable_and_disable_elements()
            self.refresh()

    def remove_curr_img(self) -> None:
        """Called after File > Remove File.

        Removes current image from `IMAGE_LIST`.

        :returns: None"""
        if len(globs.IMAGE_LIST) == 0:
            print("Can't remove from empty list!")
            return
        del globs.IMAGE_LIST[globs.IMAGE_LIST.index]
        if len(globs.IMAGE_LIST) == 0:
            # TODO: Could remove and then disable GUI elements
            self.disable_elements()
            return
        self.refresh()

    def next_img(self):
        """Called when Next button is clicked.

        Advance index and render image and sliders."""
        globs.IMAGE_LIST.next()
        self.refresh()

    def previous_img(self):
        """Called when Previous button is clicked.

        Decrement index and render image and sliders."""
        globs.IMAGE_LIST.previous()
        self.refresh()

    def rotate_x(self):
        """Called any time the user updates the x slider.

        Handle x slider movement by rendering image and setting `x_rotation_label`."""
        curr_mri_image: MRIImage = globs.IMAGE_LIST[globs.IMAGE_LIST.index]
        x_slider_val: int = self.x_slider.value()
        curr_mri_image.theta_x = x_slider_val
        render_curr_slice()
        self.x_rotation_label.setText(f'X rotation: {x_slider_val}°')

    def rotate_y(self):
        """Called any time the user updates the y slider.

        Handle y slider movement by rendering image and setting `y_rotation_label`."""
        curr_mri_image: MRIImage = globs.IMAGE_LIST[globs.IMAGE_LIST.index]
        y_slider_val: int = self.y_slider.value()
        curr_mri_image.theta_y = y_slider_val
        render_curr_slice()
        self.y_rotation_label.setText(f'Y rotation: {y_slider_val}°')

    def rotate_z(self):
        """Called any time the user updates the z slider.

        Handle z slider movement by rendering image and setting `z_rotation_label`."""
        curr_mri_image: MRIImage = globs.IMAGE_LIST[globs.IMAGE_LIST.index]
        z_slider_val: int = self.z_slider.value()
        curr_mri_image.theta_z = z_slider_val
        render_curr_slice()
        self.z_rotation_label.setText(f'Z rotation: {z_slider_val}°')

    def slice_update(self):
        """Called any time the user updates the slice slider.

        Handle slice slider movement by rendering image and setting `slice_num_label`."""
        curr_mri_image: MRIImage = globs.IMAGE_LIST[globs.IMAGE_LIST.index]
        slice_slider_val: int = self.slice_slider.value()
        curr_mri_image.slice_z = slice_slider_val
        render_curr_slice()
        self.slice_num_label.setText(f'Slice: {slice_slider_val}')

    def reset_settings(self):
        """Called when Reset is clicked.

        Resets rotation values and slice num to 0 for the current image, then re-renders image and sliders."""
        curr_mri_image: MRIImage = globs.IMAGE_LIST[globs.IMAGE_LIST.index]
        curr_mri_image.theta_x = 0
        curr_mri_image.theta_y = 0
        curr_mri_image.theta_z = 0
        curr_mri_image.slice_z = 0
        self.refresh()

    def refresh(self) -> None:
        """Refresh everything (i.e., image and sliders).

        Called on window switch and image switch."""
        render_curr_slice()
        self.render_all_sliders()


class CircumferenceWindow(QMainWindow):
    """Displayed after pressing Apply in MainWindow.

    Displays the same MRI slice as in MainWindow and the computed circumference.

    No sliders but displays rotation & slice values.

    There should be only one instance of this class."""

    def __init__(self):
        """Load circumference.ui and connect GUI events to methods/functions."""
        super(CircumferenceWindow, self).__init__()
        loadUi(str(Path.cwd() / 'src' / 'GUI' / 'circumference.ui'), self)
        self.enable_and_disable_elements()
        self.action_exit.triggered.connect(exit)
        self.action_github.triggered.connect(
            lambda: webbrowser.open(GITHUB_LINK))
        self.action_documentation.triggered.connect(
            lambda: webbrowser.open(DOCUMENTATION_LINK))
        self.action_export_png.triggered.connect(
            lambda: export_curr_slice_as_img('png'))
        self.action_export_jpg.triggered.connect(
            lambda: export_curr_slice_as_img('jpg'))
        self.action_export_bmp.triggered.connect(
            lambda: export_curr_slice_as_img('bmp'))
        self.action_export_ppm.triggered.connect(
            lambda: export_curr_slice_as_img('ppm'))
        self.action_export_xbm.triggered.connect(
            lambda: export_curr_slice_as_img('xbm'))
        self.action_export_xpm.triggered.connect(
            lambda: export_curr_slice_as_img('xpm'))
        self.adjust_slice_button.clicked.connect(goto_main)
        self.show()

    def enable_and_disable_elements(self):
        """Called when switching from MainWindow to CircumferenceWindow (i.e., Apply button is clicked).

        Needs only handle the things that are different from MainWindow."""
        self.action_open.setEnabled(False)
        self.action_export_csv.setEnabled(True)


def render_curr_slice() -> None:
    """Resamples the currently selected MRIImage using rotation and slice settings,
    then renders the resulting slice in the GUI.

    Also sets text for `image_num_label` and file path in the status bar tooltip.

    If `curr_window == CIRCUMFERENCE_WINDOW`, also calls `imgproc.contour()` and overlays
    the contour on top of the image. Note `==`, not `isinstance()`, because there should
    be only one global instance of `CircumferenceWindow`.

    NOTE: This function relies on the object names `image` and `image_num_label` being
    the same for `MainWindow` and `CircumferenceWindow` in the `.ui` files.

    :return: `None`"""
    curr_window = STACKED_WIDGET.currentWidget()
    curr_mri_image: MRIImage = globs.IMAGE_LIST[globs.IMAGE_LIST.index]
    index: int = globs.IMAGE_LIST.index
    rotated_slice: sitk.Image = curr_mri_image.resample()

    slice_np: np.ndarray = sitk.GetArrayFromImage(rotated_slice)
    slice_np = np.ndarray.transpose(slice_np)
    q_img = qimage2ndarray.array2qimage(slice_np, normalize=True)

    if curr_window == CIRCUMFERENCE_WINDOW:
        # Don't retranspose here even though QImage and np treat w and h differently
        # This keeps the shape of the QImage and np array the same,
        # i.e. q_img.size().width() == binary_contour_slice.shape[0]
        binary_contour_slice: np.ndarray = imgproc.contour(
            rotated_slice, False)
        imgproc.mask_QImage(q_img, binary_contour_slice,
                            imgproc.string_to_QColor(settings.CONTOUR_COLOR))

    q_pixmap: QPixmap = QPixmap(q_img)

    curr_window.image.setPixmap(q_pixmap)
    curr_window.image_num_label.setText(
        f'Image {index + 1} of {len(globs.IMAGE_LIST)}')
    curr_window.image.setStatusTip(str(
        curr_mri_image.path if settings.IMAGE_STATUS_BAR_SHOWS_FULL_PATH else curr_mri_image.path.name))


def export_curr_slice_as_img(extension: str):
    """Called when an Export as image menu item is clicked.

    Exports `curr_window.image` to `settings.IMG_DIR`.

    Filename has format <file_name>_[contoured_]<theta_x>_<theta_y>_<theta_z>_<slice>.<extension>

    contoured_ will be in the name if `current_window == CIRCUMFERENCE_WINDOW`.

    Supported formats in this function are the ones supported by QPixmap,
    namely BMP, JPG, JPEG, PNG, PPM, XBM, XPM.

    NOTE: This function relies on the object name `image` being
    the same for `MainWindow` and `CircumferenceWindow` in the `.ui` files.

    :return: `None`"""
    curr_window = STACKED_WIDGET.currentWidget()
    curr_mri_image: MRIImage = globs.IMAGE_LIST[globs.IMAGE_LIST.index]
    file_name = globs.IMAGE_LIST.index + \
        1 if settings.EXPORTED_FILE_NAMES_USE_INDEX else curr_mri_image.path.name
    theta_x: int = curr_mri_image.theta_x
    theta_y: int = curr_mri_image.theta_y
    theta_z: int = curr_mri_image.theta_z
    slice_z: int = curr_mri_image.slice_z
    path: str = str(
        settings.IMG_DIR / f"{file_name}_{'contoured_' if curr_window == CIRCUMFERENCE_WINDOW else ''}{theta_x}_{theta_y}_{theta_z}_{slice_z}.{extension}")
    curr_window.image.pixmap().save(path, extension)


def goto_circumference() -> None:
    """Called when MainWindow's Apply button is clicked.

    From MainWindow, switch to CircumferenceWindow.

    Enable and disable CircumferenceWindow GUI elements.

    Compute circumference and update slice settings.

    Re-render contoured MRI slice.

    :return: `None`"""
    STACKED_WIDGET.setCurrentWidget(CIRCUMFERENCE_WINDOW)
    curr_mri_image: MRIImage = globs.IMAGE_LIST[globs.IMAGE_LIST.index]
    CIRCUMFERENCE_WINDOW.enable_and_disable_elements()
    render_curr_slice()
    # TODO: This is duplicated work since render_curr_slice already does contour and resample
    # Could easily make render_curr_slice return the contour
    circumference: float = imgproc.length_of_contour(
        imgproc.contour(curr_mri_image.resample()))
    CIRCUMFERENCE_WINDOW.circumference_label.setText(
        f'Circumference: {circumference}')
    CIRCUMFERENCE_WINDOW.slice_settings_text.setText(
        f'X rotation: {curr_mri_image.theta_x}°\nY rotation: {curr_mri_image.theta_y}°\nZ rotation: {curr_mri_image.theta_z}°\nSlice: {curr_mri_image.slice_z}')


def goto_main() -> None:
    """Called when CircumferenceWindow's Adjust button is clicked.

    From CircumferenceWindow, switch to MainWindow.

    Enables and disables MainWindow GUI elements.

    :return: `None`"""
    STACKED_WIDGET.setCurrentWidget(MAIN_WINDOW)
    render_curr_slice()
    MAIN_WINDOW.enable_and_disable_elements()


def main() -> None:
    """Main entrypoint of GUI."""
    parse_gui_cli()

    # See MainWindow.test for an example of how to access a resource
    # This import can't go at the top because parse_gui_cli has to get THEME_NAME before the import
    importlib.import_module(f'src.GUI.themes.{settings.THEME_NAME}.resources')

    if not (Path.cwd() / settings.IMG_DIR).exists():
        (Path.cwd() / settings.IMG_DIR).mkdir()

    app = QApplication(sys.argv)
    # This puts arrow buttons on the sliders but makes sliding stop early sometimes?
    # app.setStyle('Fusion')

    with open(globs.THEME_DIR / settings.THEME_NAME / f'stylesheet.qss', 'r') as f:
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
    STACKED_WIDGET.setMinimumWidth(DEFAULT_WIDTH)
    STACKED_WIDGET.setMinimumHeight(DEFAULT_HEIGHT)
    STACKED_WIDGET.show()

    try:
        sys.exit(app.exec())
    except:
        if settings.DEBUG:
            print("Exiting")


if __name__ == "__main__":
    main()

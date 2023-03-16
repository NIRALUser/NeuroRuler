# Dependencies

We use `pip` to manage dependencies. Install them with `pip install -r requirements.txt`.

## [SimpleITK](https://simpleitk.readthedocs.io/en/master/) (`sitk`)

For image processing.

### I/O, 3D rotation, and slicing

Most of this code is in [`mri_image.py`](https://github.com/COMP523TeamD/HeadCircumferenceTool/blob/main/src/utils/mri_image.py).

#### Example

```py
import SimpleITK as sitk
import numpy as np

# Read in a file 
reader: sitk.ImageFileReader = sitk.ImageFileReader()
reader.SetFileName('some path')
mri_3d: sitk.Image = reader.Execute()

# Get its dimensions
dimensions: tuple = mri_3d.GetSize() 

# 3D rotation setup
theta_x, theta_y, theta_z = 30, 45, 90
euler_3d_transform: sitk.Euler3DTransform = sitk.Euler3DTransform()
euler_3d_transform.SetCenter(mri_3d.TransformContinuousIndexToPhysicalPoint(
            [((dimension - 1) / 2.0) for dimension in dimensions]))
euler_3d_transform.SetRotation(theta_x, theta_y, theta_z) 

# 3D rotate
rotated_3d: sitk.Image = sitk.Resample(mri_3d, euler_3d_transform)

# 2D slice
slice_z = 50
rotated_slice: sitk.Image = rotated_3d[:, :, slice_z]

# Convert to numpy array
# NOTE: GetArrayFromImage returns a transpose of the sitk representation!
slice_np: np.ndarray = sitk.GetArrayFromImage(rotated_slice)

# Retranspose
# This returns a view of the array with axes transposed but doesn't modify the internal memory
slice_np = np.transpose(slice_np)
```

### Filtering

See [`contour()`](https://github.com/COMP523TeamD/HeadCircumferenceTool/blob/main/src/utils/imgproc.py), which produces a binary (0|1) `np` array with only elements on the contour = 1.

### Setup for Jupyter notebooks and other resources

This is not necessary for anything in [`src/`](https://github.com/COMP523TeamD/HeadCircumferenceTool/tree/main/src).

https://simpleitk.org/TUTORIAL/

- This links to setup instructions.
- Also links to a bunch of tutorial Jupyter notebook files.
- But what's in [`src/`](https://github.com/COMP523TeamD/HeadCircumferenceTool/tree/main/src) should suffice for this project.

### File formats supported

https://simpleitk.readthedocs.io/en/master/IO.html

## Numpy (`np`)

For image processing and arc length calculation.

In the [SimpleITK](#simpleitk-sitk) section, we converted the `sitk` representation to a `np` array.

We also re-transposed the `np` array to match the `sitk` representation.

From here, we do two things: [image visualization in GUI](#image-visualization) and [arc length computation](#opencv).

## Opencv

For arc length calculation from a `np` array representing a binary contour.

First, read through [contours](https://docs.opencv.org/4.x/d4/d73/tutorial_py_contours_begin.html) (easy to understand) and [findContours](https://docs.opencv.org/4.x/d3/dc0/group__imgproc__shape.html#gadf1ad6a0b82947fa1fe3c3d497f260e0) (full documentation).

Then see [`length_of_contour()`](https://github.com/COMP523TeamD/HeadCircumferenceTool/blob/main/src/utils/imgproc.py), which produces a `float` from a binary contour.

## [PyQt6](https://doc.qt.io/qtforpython/)

For GUI (View and Controller).

### QtDesigner

For drag-and-drop GUI design. Generates [`main.ui`](https://github.com/COMP523TeamD/HeadCircumferenceTool/blob/main/src/GUI/main.ui) and [`circumference.ui`](https://github.com/COMP523TeamD/HeadCircumferenceTool/blob/main/src/GUI/circumference.ui), which are then loaded into Python code.

Install it [here](https://build-system.fman.io/qt-designer-download).

Then open the `.ui` files in QtDesigner. You'll get the idea.

### Controller stuff

There isn't a `Controller` class.

QtDesigner allows you to assign names to elements.

Then these elements are accessible from code.

See [`src/GUI/main.py`](https://github.com/COMP523TeamD/HeadCircumferenceTool/blob/main/src/GUI/main.py). 

Specifically, see `MainWindow.__init__()` for connecting functions to elements.

See `MainWindow.rotate_x()` for an example of setting elements and getting values of elements.

### StackedWidget

For switching between the two windows `MAIN_WINDOW` and `CIRCUMFERENCE_WINDOW`.

### Layout

Laying out elements in horizontal and vertical layouts allows the GUI elements to resize themselves when the user resizes the window.

If you're making a new window, then right click outside any element in QtDesigner and click Layout. This will allow you to lay out all elements.

### Image visualization

See `MainWindow.render_curr_slice()`.

Specifically, note that we use `qimage2ndarray.gray2qimage()` to convert a `np` slice to a `QImage` that is displayed in the image, which is a `QLabel`.

### Other resources

[YouTube playlist](https://www.youtube.com/watch?v=Vde5SH8e1OQ&list=PLzMcBGfZo4-lB8MZfHPLTEHO9zJDDLpYj)

- He exports Python code from QtDesigner and edits the raw Python code, which I think is a terrible approach. But the videos are otherwise great.

[Documentation](https://doc.qt.io/qtforpython/)

### Miscellaneous

[No major differences](https://www.pythonguis.com/faq/pyqt5-vs-pyqt6/#:~:text=As%20we've%20discovered%2C%20there,d%20suggest%20starting%20with%20PyQt6) between PyQt5 and PyQt6.

PySide6 is more "official" than PyQt6, I think. Official documentation always references PySide6. But there are also [no major differences](https://www.pythonguis.com/faq/pyqt6-vs-pyside6/).

Switching to PySide6 broke [window switching](#stackedwidget), and I couldn't figure it out.

qimage2ndarray helps us avoid this, but if rendering `QPixmap` from a `np` array, note that the two libraries treat `w` and `h` differently.

```py
import numpy as np
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QMainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        pass
    
    def test(self):
        slice_np: np.ndarray = np.array([[65535, 0, 0, 0], [0, 0, 0, 65535]], dtype='uint16')
        # Note reversed ordering
        qImg: QImage = QImage(slice_np.data, slice_np.shape[1], slice_np.shape[0], QImage.Format.Format_Grayscale16)
        self.image.setPixmap(QPixmap(qImg)) 
```

![](https://user-images.githubusercontent.com/69875698/224999132-0f722c08-3a97-45b7-b2c2-ec2bd8580405.png)

## [qimage2ndarray](http://hmeine.github.io/qimage2ndarray/)

For [image visualization in PyQt GUI](#image-visualization).

[GitHub](https://github.com/hmeine/qimage2ndarray)

[Documentation](http://hmeine.github.io/qimage2ndarray/) (very short)

In [`src/GUI/main.py`](https://github.com/COMP523TeamD/HeadCircumferenceTool/blob/main/src/main.py), see `MainWindow.render_curr_slice()`.

## Matplotlib, ipywidgets

We used these to render interactive `sitk` images in Jupyter notebooks, but they're not necessary anymore.

See [`SimpleITK.ipynb`](https://github.com/COMP523TeamD/HeadCircumferenceTool/blob/main/Playground/SITK/SimpleITK.ipynb) and [`processing.ipynb`](https://github.com/COMP523TeamD/HeadCircumferenceTool/blob/main/Playground/imgproc/processing.ipynb).

## [Argparse](https://docs.python.org/3/library/argparse.html)

For parsing CLI arguments.

See [`parse_cli.py`](https://github.com/COMP523TeamD/HeadCircumferenceTool/blob/main/src/utils/parse_cli.py).

## pytest

For unit testing. See tests/.

## Not dependencies (built-in) but worth noting

### warnings, functools

Allow us to mark functions `@deprecated`.

See [`globs.py`](https://github.com/COMP523TeamD/HeadCircumferenceTool/blob/main/src/utils/globs.py).

### [pathlib](https://pathlib.readthedocs.io/en/pep428/)

For maintaining cross-platformness when working with paths.

Specifically, paths on macOS and Linux are like `~/Documents/GitHub/...`

On Windows, it's something like `C:\\idk\how\Windows\works`

Always build a `Path` using the `Path` capabilities, then when a `str` is needed, apply `str()` to convert at the end.

Use the `/` operator to build up a path.

For example, see this code from [`globs.py`](https://github.com/COMP523TeamD/HeadCircumferenceTool/blob/main/src/utils/globs.py).

```py
from pathlib import Path
from src.utils.mri_image import MRIImageList, MRIImage

SUPPORTED_EXTENSIONS: tuple = ('*.nii.gz', '*.nii', '*.nrrd')
# Use / operator instead of str '/' or '\' (would cause cross-platform inconsistencies)
EXAMPLE_DATA_DIR: Path = Path.cwd() / 'ExampleData'
EXAMPLE_IMAGES: list[MRIImage] = []

for type in SUPPORTED_EXTENSIONS:
    for path in EXAMPLE_DATA_DIR.glob(type):
        # The MRIImage constructor takes a Path argument
        # But if it took str, then you would just do str(path) here
        EXAMPLE_IMAGES.append(MRIImage(path))
```

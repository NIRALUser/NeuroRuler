.. _dependencies:

############
Dependencies
############

.. topic:: Overview

    This page describes what our dependencies are for and how to use them.
    Example code and links to related source code are provided.

    We use pip to manage dependencies. Install them with :code:`pip install -r requirements.txt`.

    :Date: |today|

.. contents::
    :depth: 3

SimpleITK (:code:`sitk`)
########################

For image processing.

I/O, 3D rotation, and slicing
=============================

Most of this code is in `mri_image.py <_modules/src/utils/mri_image.html>`_. A lot of it is scattered
throughout the project though.

.. code-block:: python
    :linenos:

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
    # NOTE: GetArrayFromImage returns the transpose of the sitk representation!
    slice_np: np.ndarray = sitk.GetArrayFromImage(rotated_slice)
 
    # Retranspose
    # This returns a view of the array with axes transposed but doesn't modify the internal memory
    slice_np = np.transpose(slice_np)

.. warning:: sitk.GetArrayFromImage() returns the transpose of the sitk representation!

Filtering
=========

.. currentmodule:: src.utils.imgproc
.. autofunction:: contour

File formats supported
======================

See `<https://simpleitk.readthedocs.io/en/master/IO.html>`_.

Fiji & tutorial notebooks
=========================

See `<https://simpleitk.org/TUTORIAL>`_ for setup instructions (installing the external image viewer Fiji
used in some of our :code:`.ipynb` files) and a bunch of tutorial Jupyter notebook files, most of which
are too advanced for this project. What's already in `src/ <src.html>`_ should suffice for this project.

Resources
=========

`<https://simpleitk.readthedocs.io/en/master/>`_

numpy (:code:`np`)
##################

For image processing and arc length calculation.

In the `SimpleITK <#simpleitk-sitk>`_ section, we converted the :code:`sitk` representation to a :code:`np`
array. We also re-transposed the :code:`np` array to match the :code:`sitk` representation.

From here, we do two things: `image visualization in GUI <#image-visualization>`_ and `arc length computation <#opencv>`_.

opencv
######

For arc length calculation from a :code:`np` array representing a binary contour.

First, read through `Contours: Getting Started <https://docs.opencv.org/4.x/d4/d73/tutorial_py_contours_begin.html>`_ (easy to understand)
and `findContours <https://docs.opencv.org/4.x/d3/dc0/group__imgproc__shape.html#gadf1ad6a0b82947fa1fe3c3d497f260e0>`_ (full documentation).

.. currentmodule:: src.utils.imgproc
.. autofunction:: length_of_contour

PyQt6
#####

For GUI. Serves the purpose of View and Controller.

QtDesigner
==========

For drag-and-drop GUI design. Generates :code:`.ui` files (pretty much XML) which are then loaded into Python code.

`Install it <https://build-system.fman.io/qt-designer-download>`_. In QtDesigner, open `main.ui <https://github.com/COMP523TeamD/HeadCircumferenceTool/blob/main/src/GUI/main.ui>`_ and `circumference.ui <https://github.com/COMP523TeamD/HeadCircumferenceTool/blob/main/src/GUI/circumference.ui>`_. You'll get the idea.

Controller stuff
================

There isn't a Controller class. Controller stuff is done in `src/GUI/main.py <_modules/src/GUI/main>`_.

QtDesigner lets you assign names to elements. Then these variables are accessible from code.

See `MainWindow.__init__ <_modules/src/GUI/main.html#MainWindow>`_ for an example of
connecting GUI events to functions.

See `rotate_x()` for an example of getting and setting values in the GUI.

.. currentmodule:: src.GUI.main.MainWindow
.. autofunction:: rotate_x

`[source] <_modules/src/GUI/main.html#MainWindow.rotate_x>`_

StackedWidget
=============

For switching between the two windows :code:`MAIN_WINDOW` and :code:`CIRCUMFERENCE_WINDOW`.

.. currentmodule:: src.GUI.main
.. autofunction:: main

Layout
======

Laying out elements in horizontal and vertical layouts allows the GUI elements to resize themselves when the user resizes the window.

If you're making a new window, right click outside any element in QtDesigner and click Layout. This will allow you to lay out all elements.

Image visualization
===================

.. currentmodule:: src.GUI.main.MainWindow
.. autofunction:: render_curr_slice

`[source] <_modules/src/GUI/main.html#MainWindow.render_curr_slice>`_

Other resources
===============

`YouTube playlist <https://www.youtube.com/watch?v=Vde5SH8e1OQ&list=PLzMcBGfZo4-lB8MZfHPLTEHO9zJDDLpYj>`_

* He exports Python code from QtDesigner and edits the raw Python code, which I think is a terrible approach. But the videos are otherwise great.

`Official documentation <https://doc.qt.io/qtforpython/>`_

Alternatives
============

`No major differences <https://www.pythonguis.com/faq/pyqt5-vs-pyqt6/#:~:text=As%20we've%20discovered%2C%20there,d%20suggest%20starting%20with%20PyQt6>`_ between PyQt5 and PyQt6.

`No major differences <https://www.pythonguis.com/faq/pyqt6-vs-pyside6/>`_ between PySide6 and PyQt6. PySide6 is more official than PyQt6, and official documentation always references PySide6.
However, switching to PySide6 broke window switching, and I couldn't figure it out.

.. warning:: Note QImage and numpy treat width and height differently!

    qimage2ndarray helps us avoid this problem, but just FYI.


    .. code-block:: python
        :linenos:

        import numpy as np
        from PyQt6.QtGui import QPixmap, QImage
        from PyQt6.QtWidgets import QMainWindow

        class MainWindow(QMainWindow):
            def __init__(self):
                pass

            def test(self):
                slice_np: np.ndarray = np.array([[65535, 0, 0, 0],
                                                 [0, 0, 0, 65535]], dtype='uint16')
                # Note reversed ordering
                qImg: QImage = QImage(slice_np.data, slice_np.shape[1], slice_np.shape[0], QImage.Format.Format_Grayscale16)
                self.image.setPixmap(QPixmap(qImg)) 

    .. image:: _static/qimage_numpy.png
        :width: 200px
        :align: center
        :alt: Reversed width and height between QImage and numpy

qimage2ndarray
##############

For `image visualization <#image-visualization>`_ in PyQt GUI.

`GitHub <https://github.com/hmeine/qimage2ndarray>`_ and `Documentation <http://hmeine.github.io/qimage2ndarray/>`_ (very brief).

.. currentmodule:: src.GUI.main.MainWindow
.. autofunction:: render_curr_slice

`[source] <_modules/src/GUI/main.html#MainWindow.render_curr_slice>`_

matplotlib, ipywidgets
######################

We used these to render interactive :code:`sitk` images in Jupyter notebooks, but this isn't necessary anymore.

argparse
########

For parsing CLI arguments.

.. currentmodule:: src.utils.parse_cli
.. autofunction:: parse_gui_cli

pytest
######

For unit testing.

warnings, functools
###################

Allow us to mark functions :code:`@deprecated`.

.. currentmodule:: src.utils.globs
.. autofunction:: deprecated

pathlib
#######

For maintaining cross-platformness when working with paths.

Specifically, Posix paths look like :code:`Users/jesse/Documents/GitHub/...`,
whereas Windows paths look like :code:`C:\\idk\\how\\Windows\\works\\...`.

Always build up a :code:`Path` using the :code:`Path` capabilities (:code:`/` operator).
Then when a :code:`str` is needed, apply :code:`str()` to convert at the end.

See the `documentation <https://pathlib.readthedocs.io/en/pep428/>`_ for example code. Also see this code from `src/utils/globs.py <_modules/src/utils/globs.html>`_.

.. code-block:: python
        :linenos:

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

sphinx, setuptools
##################

For automatically generating these documentation pages.

`Read the Docs tutorial <https://docs.readthedocs.io/en/stable/tutorial/>`_ (some steps caused deployment errors 😔)
and `YouTube video <https://www.youtube.com/watch?v=BWIrhgCAae0>`_ about Sphinx.

Steps for building from scratch
===============================

.. note:: This won't have to be done again for this project, just here for reference.

.. code-block:: text

    pip install sphinx
    pip install python-docs-theme
    mkdir docs
    cd docs
    sphinx-quickstart

Type `n` for the first question, which asks about splitting source and build directories [#f1]_.

Copy over :code:`docs/conf.py` (install another theme with pip and modify :code:`html_theme` if you want),
:code:`docs/requirements.txt`, :code:`.readthedocs.yaml`, :code:`pyproject.toml`, and :code:`setup.py` from the
`HCT repo <https://github.com/COMP523TeamD/HeadCircumferenceTool>`_,
overwriting if necessary. The root :code:`requirements.txt` and :code:`requirements_dev.txt` might also need to include
setuptools, but I'm not certain.

Make sure :code:`src/__init__.py` exists, along with :code:`.../__init__.py` files for any package that
you want to auto-generate documentation for.

.. note:: Current working directory should still be :code:`docs/`

.. code-block:: text

    sphinx-apidoc -o . ../src       # Copy files from ../src to . (docs/)
    make html

`docs/_build/html/index.html` should now contain the local version of the documentation pages.

Now follow the Read the Docs tutorial starting from `Sign up for Read the Docs <https://docs.readthedocs.io/en/stable/tutorial/#sign-up-for-read-the-docs>`_.
You can end at Checking the first build. To set up CDD (continuous documentation deployment), check
`Permissions for connected accounts <https://docs.readthedocs.io/en/stable/guides/git-integrations.html>`_ and
follow the `Provider-specific instructions steps <https://docs.readthedocs.io/en/stable/guides/git-integrations.html#provider-specific-instructions>`_.

Lastly, modify `docs/index.rst`, which is the homepage.

RST formatting
==============

See the `source code <https://github.com/COMP523TeamD/HeadCircumferenceTool/blob/main/docs/dependencies.rst>`_
for this page and `<https://thomas-cokelaer.info/tutorials/sphinx/rest_syntax.html>`_.

Other resources
===============

`YouTube video <https://www.youtube.com/watch?v=BWIrhgCAae0>`_ about Sphinx

* Where I got the above steps from

.. rubric:: Footnotes

.. [#f1] Not sure if this actually needs to be `n`, but I'm not messing around with it any more.

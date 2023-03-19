.. _dependencies:

############
Dependencies
############

.. topic:: Overview

    This page describes what our dependencies are for and how to use them.
    Links to our related source code are provided.

    Install dependencies with :code:`pip install -r requirements.txt`.

    Generally, the commands here should be updated if there's a change. But if some command doesn't work,
    apply the :code:`-h` command line option, and you should be able to figure it out.

.. contents::
    :depth: 3

.. _SimpleITK:

SimpleITK (:code:`sitk`)
########################

For image processing.

.. _SimpleITKIO:

I/O, 3D rotation, and slicing
=============================

Most of this code is in `mri_image.py <_modules/src/utils/mri_image.html>`_. A lot of it is scattered
throughout the project though.

.. code-block:: python
    :linenos:

    import SimpleITK as sitk
    import numpy as np
    from pathlib import Path
 
    # Read in a file 
    reader: sitk.ImageFileReader = sitk.ImageFileReader()
    reader.SetFileName(str(Path.cwd() / 'some' / 'path' / 'to' / '3D image'))
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

.. warning:: :code:`sitk.GetArrayFromImage()` returns the transpose of the :code:`sitk` representation!

.. _SimpleITKFiltering:

Filtering
=========

.. currentmodule:: src.utils.imgproc
.. autofunction:: contour

.. _SimpleITKFileFormats:

File formats supported
======================

`<https://simpleitk.readthedocs.io/en/master/IO.html>`_

.. _SimpleITKFiji:

Fiji & tutorial notebooks
=========================

See `<https://simpleitk.org/TUTORIAL>`_ for setup instructions (installing the external image viewer Fiji
used in some of our :code:`.ipynb` files) and a bunch of tutorial Jupyter notebook files, most of which
are too advanced for this project. What's already in `src/ <src.html>`_ should suffice for this project.

.. _SimpleITKResources:

Resources
=========

`<https://simpleitk.readthedocs.io/en/master/>`_

.. _numpy:

numpy (:code:`np`)
##################

For image processing and arc length calculation.

In the :ref:`SimpleITK` section, we converted the :code:`sitk` representation to a :code:`np`
array. We also re-transposed the :code:`np` array to match the :code:`sitk` representation.

From here, we do two things: :ref:`PyQt6ImageVisualization` and :ref:`arc length computation <opencv>`.

.. _opencv:

opencv
######

For arc length calculation from a :code:`np` array representing a binary contour.

First, read through `Contours: Getting Started <https://docs.opencv.org/4.x/d4/d73/tutorial_py_contours_begin.html>`_ (easy to understand)
and `findContours <https://docs.opencv.org/4.x/d3/dc0/group__imgproc__shape.html#gadf1ad6a0b82947fa1fe3c3d497f260e0>`_ (full documentation).

.. currentmodule:: src.utils.imgproc
.. autofunction:: length_of_contour

.. _PyQt6:

PyQt6
#####

For GUI. Serves the purpose of View and Controller. Drag-and-drop GUI design using :ref:`PyQt6QtDesigner`.
Easy styling with :code:`.qss` stylesheets and resource (icon) management with :code:`.qrc` files, both of
which can be even more easily managed using :ref:`BreezeStyleSheets`.

.. _PyQt6QtDesigner:

QtDesigner
==========

For drag-and-drop GUI design. Generates :code:`.ui` files (pretty much XML) which are then loaded into Python code.

`Install it <https://build-system.fman.io/qt-designer-download>`_. In QtDesigner, open
`main.ui <https://github.com/COMP523TeamD/HeadCircumferenceTool/blob/main/src/GUI/main.ui>`_ and
`circumference.ui <https://github.com/COMP523TeamD/HeadCircumferenceTool/blob/main/src/GUI/circumference.ui>`_.
You'll get the idea.

.. _PyQt6Controller:

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

.. _PyQt6QStackedWidget:

QStackedWidget
==============

For switching between the two windows :code:`MAIN_WINDOW` and :code:`CIRCUMFERENCE_WINDOW`.
Though it's not in the :code:`.ui` files, :code:`MAIN_WINDOW` and :code:`CIRCUMFERENCE_WINDOW`
are inside a top-level :code:`QStackedWidget`.

.. currentmodule:: src.GUI.main
.. autofunction:: main

`QStackedWidget documentation <https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QStackedWidget.html>`_

.. _PyQt6Layout:

Layout
======

Laying out elements in horizontal and vertical layouts allows the GUI elements to
resize themselves when the user resizes the window.

If you're making a new window,
right click outside any element in QtDesigner and click Layout.
This will allow you to lay out all elements.

.. _PyQt6ImageVisualization:

Image visualization
===================

.. currentmodule:: src.GUI.main
.. autofunction:: render_curr_slice

`[source] <_modules/src/GUI/main.html#render_curr_slice>`_

.. _PyQt6QRC:

QRC file
========

Used to manage resources (application icons in :code:`.svg`, :code:`.png`, etc. formats).

See this short `YouTube video <https://www.youtube.com/watch?v=LG4QgG9AZkE>`_ about QRC files.

:ref:`BreezeStyleSheets` generates QRC files and compiled Python resource files that we can use. That section of
this page is very closely related. Read that next if you're working on styling the GUI.

.. currentmodule:: src.GUI.main.MainWindow
.. autofunction:: test_show_resource

`[source] <_modules/src/GUI/main.html#MainWindow.test_show_resource>`_

.. See the `PyQt documentation <https://doc.qt.io/qtforpython/tutorials/basictutorial/qrcfiles.html#changes-in-the-code>`_
.. for how to access resources once imported.

.. _PyQt6Resources:

Other resources
===============

`YouTube playlist <https://www.youtube.com/watch?v=Vde5SH8e1OQ&list=PLzMcBGfZo4-lB8MZfHPLTEHO9zJDDLpYj>`_

* He exports Python code from :ref:`PyQt6QtDesigner` and edits the raw Python code, which I think is a terrible approach. It's better to load the :code:`.ui` files from within Python. But the videos are otherwise great.

`Qt for Python <https://doc.qt.io/qtforpython-6/>`_

* This link is "qtforpython-6". It references :code:`PySide6`, but mostly everything is the same, as mentioned below. If you Google a keyword, you might get a result on the "qtforpython-5" site. There are some small (mostly naming) differences, so make sure you're on the the correct site.

.. _PyQt6Alternatives:

Alternatives
============

`No major differences <https://www.pythonguis.com/faq/pyqt5-vs-pyqt6/#:~:text=As%20we've%20discovered%2C%20there,d%20suggest%20starting%20with%20PyQt6>`_ between PyQt5 and PyQt6.

`Also no major differences <https://www.pythonguis.com/faq/pyqt6-vs-pyside6/>`_ between PySide6 and PyQt6. PySide6 is more official than PyQt6, and official documentation always references PySide6.
However, switching to PySide6 broke window switching, and I couldn't figure it out.

.. warning:: Note QImage and :ref:`numpy` treat width and height differently!

    :ref:`qimage2ndarray` helps us avoid this problem, but just FYI.

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
                q_img: QImage = QImage(slice_np.data, slice_np.shape[1], slice_np.shape[0],
                                      QImage.Format.Format_Grayscale16)
                self.image.setPixmap(QPixmap(q_img)) 

            # Rest of the code omitted

    .. image:: _static/qimage_numpy.png
        :width: 300px
        :align: center
        :alt: Reversed width and height between QImage and numpy

.. _qimage2ndarray:

qimage2ndarray
##############

For :ref:`PyQt6ImageVisualization` in PyQt GUI.

Specifically, qimage2ndarray converts a :code:`np` array to a :code:`QImage` that can be displayed in a PyQt GUI,
as the name implies.

`GitHub <https://github.com/hmeine/qimage2ndarray>`_ and `Documentation <http://hmeine.github.io/qimage2ndarray/>`_ (very brief).

.. currentmodule:: src.GUI.main
.. autofunction:: render_curr_slice

.. warning:: In :code:`src/GUI/main.py`, if :code:`import qimage2ndarray` goes before the PyQt imports (which an
    autoformatter might do), there will be a :code:`ModuleNotFoundError`.

`[source] <_modules/src/GUI/main.html#render_curr_slice>`_

.. _BreezeStyleSheets:

BreezeStyleSheets
#################

Used to generate our GUI's :code:`.qss` stylesheets and corresponding :code:`resources.py` files.

.. _BreezeStyleSheetsHowItWorks:

How it works
============

.. note:: You can skip down to :ref:`BreezeStyleSheetsInstallation` if you want. 

Skim the README in the `BreezeStyleSheets repo <https://github.com/Alexhuszagh/BreezeStyleSheets.git>`_.

In a nutshell, we edit a JSON file with hex codes and compile to a :code:`.qss` stylesheet that we can
use in our program. It also generates :ref:`QRC files <PyQt6QRC>` and compiled :code:`.py` resource files
for managing resources (icons).

.. _BreezeStyleSheetsInstallation:

Installation instructions
=========================

1. Clone our fork of the `repo <https://github.com/COMP523TeamD/BreezeStyleSheets>`_.
2. Try running :code:`python configure.py --styles=all --extensions=all --pyqt6 --resource breeze.qrc --compiled-resource breeze_resources.py`

If you get something that looks like this, then PyQt5 (specifically, the :code:`pyrcc5` command)
is not installed.

.. code-block:: text

    subprocess.CalledProcessError: Command '['pyrcc5', '/Users/jesse/Documents/GitHub/COMP523/BreezeStyleSheets/dist/qrc/breeze.qrc', '-o', '/Users/jesse/Documents/GitHub/COMP523/BreezeStyleSheets/breeze_resources.py']' returned non-zero exit status 1.

On macOS, :code:`pip install PyQt5` didn't work, so I had to do some extra stuff.

These are the the commands I ran to install PyQt5 on macOS.

.. code-block:: text

    brew install qt5
    brew link qt5 --force
    pip3 install pyqt5 --config-settings --confirm-license= --verbose

Took a while to install...

If you get any errors, these are the relevant StackOverflow links: [#f1]_ [#f2]_ [#f3]_.

.. _BreezeStyleSheetsConfiguration:

Configuration instructions
==========================

First, copy and paste one of the existing theme JSON's in :code:`theme/`. Rename it, and I'll refer
to the new name as :code:`theme_name`.

As mentioned in the `README <https://github.com/Alexhuszagh/BreezeStyleSheets#customization>`_, there's a lot of fields, but we should modify only a few.
I ran :code:`diff theme/dark.json theme/dark-green.json` [#f4]_, and the only fields that changed were these:

* :code:`"highlight"`
* :code:`"highlight:dark"`
* :code:`"highlight:alternate"`
* :code:`"view:checked"`
* :code:`"view:hover"`
* :code:`"slider:foreground"`
* :code:`"checkbox:light"`
* :code:`"scrollbar:hover"`

.. note:: You can skip a lot of the rest of this section. In our BreezeStyleSheets fork, there's a script
    `hct.py <https://github.com/COMP523TeamD/BreezeStyleSheets/blob/main/hct.py>`_ that does the rest of this.
    
    First, open `hct.py <https://github.com/COMP523TeamD/BreezeStyleSheets/blob/main/hct.py>`_ and modify
    :code:`PATH_TO_HCT_REPO_THEMES_DIR` to be :code:`.../themes` directory in your computer's HCT directory.
    
    Then run :code:`python hct.py <theme_name>`, where :code:`theme_name` is the name of the new JSON file.
    You should now be able to run the HCT GUI with the new theme.
    For now, you would just do :code:`python -m src.GUI.main -t <theme_name>`.
    
    If something changes and this documentation hasn't been updated, apply the :code:`-h` option to see how to
    apply the theme.

After making edits, run these commands to build the stylesheet, icons, and resource file for a single theme.

.. code-block:: text

    python configure.py --styles=<name of JSON> --resource custom.qrc
    python configure.py --styles=<name of JSON> --extensions=all --pyqt6 --resource custom.qrc --compiled-resource resources.py

:code:`dist/qrc/{theme_name}` should now exist. In the HCT repo, create
a new folder :code:`src/GUI/themes/{theme_name}`. Drag in :code:`dist/qrc/{theme_name}/stylesheet.qss` and :code:`resources.py`.

In :code:`resources.py`, change :code:`from PyQt5 import QtCore` to :code:`from PyQt6 import QtCore`.

Run the HCT GUI with the :code:`-t {theme_name}` option to test.
Push changes to the HCT repo and BreezeStyleSheets fork if it looks good 😊.

See :ref:`QRC file <PyQt6QRC>` for an example of how to access a resource from within code.
Since we're using compiled :code:`resource.py` files, we don't have the :code:`.svg` files in our HCT repo.
Check the BreezeStyleSheets repo for `resource names <https://github.com/Alexhuszagh/BreezeStyleSheets/tree/main/dist/qrc/dark>`_.

.. _matplotlibipywidgets:

matplotlib, ipywidgets
######################

We used these to render interactive :code:`sitk` images in Jupyter notebooks, but this isn't necessary anymore.

.. _argparse:

argparse
########

For parsing CLI arguments.

.. currentmodule:: src.utils.parse_cli
.. autofunction:: parse_gui_cli

.. _pytest:

pytest
######

For unit testing.

.. _warningsfunctools:

warnings, functools
###################

Allow us to mark functions :code:`@deprecated`.

.. currentmodule:: src.utils.globs
.. autofunction:: deprecated

.. _pathlib:

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

    THEME_DIR: Path = Path('src') / 'GUI' / 'themes'
    """themes/ directory where .qss stylesheets and resources.py files are stored."""
    THEMES: set[str] = set()
    """List of themes, i.e. the names of the directories in THEME_DIR."""
    if len(list(THEME_DIR.glob('*'))) != 0:
        for path in THEME_DIR.iterdir():
            if path.is_dir():
                THEMES.add(path.name)
    else:
        print(f'No themes discovered in {str(THEME_DIR)}. Make sure to run from .../HeadCircumferenceTool .')

.. _sphinxsetuptools:

sphinx, setuptools
##################

For automatically generating these documentation pages.

.. note:: This website is automatically updated on push, PR, etc. in the HCT repo, so you don't need to follow these steps unless you're making changes to the site and want to be able to build the website locally to review changes before pushing.

`Read the Docs tutorial <https://docs.readthedocs.io/en/stable/tutorial/>`_ (some steps caused deployment errors 😔)
and `YouTube video <https://www.youtube.com/watch?v=BWIrhgCAae0>`_ about Sphinx.

.. _sphinxBuildSite:

Build HCT site locally
======================

Your current working directory should be the HCT repo.

.. code-block:: text

    pip install sphinx
    pip install python-docs-theme
    cd docs
    make html

:code:`docs/_build/html/` will now contain the local version of the documentation pages.

.. note:: :code:`docs/_build` is gitignored.

You can open :code:`docs/_build/html/index.html` in a web browser to check out the site before pushing, which will automatically update the
website. From now on, you can just run :code:`make html` to update the html pages.

However, you will need to run :code:`sphinx-apidoc -o . ../src` from the :code:`docs/` directory
if a new package is created. Make sure :code:`__init__.py` files exist for any package you want
to be discovered.

You can edit `docs/index.rst <https://github.com/COMP523TeamD/HeadCircumferenceTool/blob/main/docs/index.rst>`_,
which is the homepage, or `docs/dependencies.rst <https://github.com/COMP523TeamD/HeadCircumferenceTool/blob/main/docs/dependencies.rst>`_, which
is this page. `Documentation <modules.html>`_ for `source code <_modules/index.html>`_ is automatically generated.

.. _sphinxBuildFromScratch:

Steps for building from scratch
===============================

.. note:: This does not have to be done for the HCT repo since setup is already complete.
    It's mostly here for my reference since there's not a lot of information about this process online and I'd forget
    how to do it.

Your current working directory should be whatever repo you want to automatically generate documentation for.

.. code-block:: text

    pip install sphinx
    pip install python-docs-theme
    mkdir docs
    cd docs
    sphinx-quickstart

Type `n` for the first question, which asks about splitting source and build directories [#f5]_.

Copy over :code:`docs/conf.py` (install another theme with pip and modify :code:`html_theme` if you want),
:code:`docs/requirements.txt`, :code:`.readthedocs.yaml`, :code:`pyproject.toml`, and :code:`setup.py` from the
`HCT repo <https://github.com/COMP523TeamD/HeadCircumferenceTool>`_,
overwriting if necessary. Modify the info inside for your purposes.
The root :code:`requirements.txt` and :code:`requirements_dev.txt` might also need to include
setuptools, but I'm not certain.

Make sure :code:`src/__init__.py` exists, along with :code:`.../__init__.py` files for any package that
you want to auto-generate documentation for.

.. note:: Current working directory should still be :code:`docs/`

.. code-block:: text

    sphinx-apidoc -o . ../src       # Generate files from ../src and put in . (docs/)
    make html

:code:`docs/_build/html/index.html` will now contain the local version of the documentation pages.
You can open it in a web browser to check it out before pushing, which will automatically update the
website. From now on, you can just run :code:`make html` to update the html pages. You don't need to run
:code:`sphinx-apidoc` unless you create a new package.

You can edit :code:`docs/index.rst`, which is the homepage.

Now follow the Read the Docs tutorial starting from `Sign up for Read the Docs <https://docs.readthedocs.io/en/stable/tutorial/#sign-up-for-read-the-docs>`_.
You can end at Checking the first build. To set up CDD (continuous documentation deployment), check
`Permissions for connected accounts <https://docs.readthedocs.io/en/stable/guides/git-integrations.html>`_ and
follow the `Provider-specific instructions steps <https://docs.readthedocs.io/en/stable/guides/git-integrations.html#provider-specific-instructions>`_.

.. _sphinxRST:

RST formatting
==============

See the `source code <https://github.com/COMP523TeamD/HeadCircumferenceTool/blob/main/docs/dependencies.rst>`_
for this page and `<https://thomas-cokelaer.info/tutorials/sphinx/rest_syntax.html>`_.

.. _sphinxResources:

Resources
===============

`YouTube video <https://www.youtube.com/watch?v=BWIrhgCAae0>`_ about Sphinx where I got a lot of these steps from.

.. _importlib:

importlib
#########

For importing modules using strings.

Specifically, if supporting multiple themes and stylesheets, then import statements will change depending
on :code:`src.utils.settings.THEME_NAME`.

For example, in :code:`src.GUI.main()`, if :code:`THEME_NAME` is :code:`'dark'`, then
the resources import statement would be

.. code-block:: python

    import src.GUI.styles.dark.resources

However, if :code:`THEME_NAME` is :code:`'light'`, then the import statement would be

.. code-block:: python

    import src.GUI.styles.light.resources

Therefore, we use importlib to control the import name there. Alternatively, we could have just one
resources file for every theme, but I think BreezeStyleSheets might re-compile resource :code:`.svg` files
based on the theme :code:`.json`.

.. rubric:: Footnotes

.. [#f1] `macOS PyQt5 install 1 <https://stackoverflow.com/questions/70961915/error-while-installing-pytq5-with-pip-preparing-metadata-pyproject-toml-did-n>`_
.. [#f2] `macOS PyQt5 install 2 <https://stackoverflow.com/questions/66546886/pip-install-stuck-on-preparing-wheel-metadata-when-trying-to-install-pyqt5>`_
.. [#f3] `macOS PyQt5 install 3 <https://stackoverflow.com/questions/73714829/pip-install-pyqt5-it-cannot-go-on/74071222#74071222>`_
.. [#f4]

.. code-block:: bash

    ❯ diff theme/dark.json theme/dark-green.json
    8,10c8,10
    <     "highlight": "#3daee9",
    <     "highlight:dark": "#2a79a3",
    <     "highlight:alternate": "#2f88b7",
    ---
    >     "highlight": "#33b833",
    >     "highlight:dark": "#2b992b",
    >     "highlight:alternate": "#1f991f",
    15,16c15,16
    <     "view:checked": "#334e5e",
    <     "view:hover": "rgba(61, 173, 232, 0.1)",
    ---
    >     "view:checked": "#325c32",
    >     "view:hover": "rgba(63, 232, 63, 0.1)",
    28c28
    <     "slider:foreground": "#3daee9",
    ---
    >     "slider:foreground": "#33b833",
    31c31
    <     "checkbox:light": "#58d3ff",
    ---
    >     "checkbox:light": "#40e640",
    33c33
    <     "scrollbar:hover": "#3daee9",
    ---
    >     "scrollbar:hover": "#33b833",

.. [#f5] Not sure if this actually needs to be `n`, but I'm not messing around with it any more.

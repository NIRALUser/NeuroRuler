"""Global variables.

Only for use in the GUI! Due to the way they're updated in mri_image.py, will likely cause bugs when doing batch processing via CLI!"""

import SimpleITK as sitk
# Causes circular import error since mri_image.py imports globs.py
# from src.utils.mri_image import MRIImage, MRIImageList

# -1 is a dummy value
IMAGE_LIST = -1
"""Type is `MRIImageList` but can't type it as that in `globs.py` due to circular import.

`.next()` and `.previous()` automatically modify `CURR_MRI_IMAGE`, `CURR_SLICE`, and `CURR_SLICE_INDEX`.

Not for use in CLI batch processing."""

# -1 is a dummy value
CURR_MRI_IMAGE = -1
"""`IMAGE_LIST`'s current `MRIImage`. Type is `MRIImage` but can't type it as that in globs.py due to circular import.

Updated after `IMAGE_LIST.next()` and `.previous()`.

Not for use in CLI batch processing."""

CURR_SLICE: sitk.Image = sitk.Image(8, 8, 0, sitk.sitkUInt8)
"""`IMAGE_LIST`'s current rotated slice.

Updated after `IMAGE_LIST.next()` and `.previous()`.

Also `CURR_MRI_IMAGE.resample()`.

Not for use in CLI batch processing."""

INDEX: int = 0
"""`IMAGE_LIST`'s current `index`.

Updated after `IMAGE_LIST.next()` and `.previous()`.

Not for use in CLI batch processing."""

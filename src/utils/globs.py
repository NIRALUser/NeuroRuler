"""Global variables"""

import SimpleITK as sitk
from src.utils.mri_image import MRIImage, MRIImageList

# These might not be needed
# global IMAGE_LIST
# global CURR_MRI_IMAGE
# global CURR_SLICE
# global CURR_SLICE_INDEX

IMAGE_LIST: MRIImageList = MRIImageList()
CURR_MRI_IMAGE: MRIImage
"""`IMAGE_LIST`'s current `MRIImage`.

Warning: Not automatically updated when calling `IMAGE_LIST.next()` or `.previous()`. Must manually adjust."""
# TODO: Could remove this variable since you have to remember to update it after updating CURR_MRI_IMAGE
# Only a minor convenience but could cause serious bugs
CURR_SLICE: sitk.Image = sitk.Image(8, 8, 0, sitk.sitkUInt8)
"""`IMAGE_LIST`'s current rotated slice.

Warning: Not automatically updated when calling `CURR_MRI_IMAGE`.resample()` or `IMAGE_LIST.next()` or `.previous()`. Must manually update this after resampling."""
# Same with this variable
CURR_SLICE_INDEX: int = 0
"""`IMAGE_LIST`'s current `index`.

Warning: Not automatically updated when calling `IMAGE_LIST.next()` or `.previous()`. Must manually update after doing so."""
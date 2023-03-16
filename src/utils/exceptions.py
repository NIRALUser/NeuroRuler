"""Custom exceptions."""


# TODO: Make __init__ accept theta_x, theta_y, theta_z, slice_num as parameters to display those to the user?
# Probably not necessary because those will be displayed in the GUI.
class ComputeCircumferenceOfInvalidSlice(Exception):
    """User attempted to compute circumference of an invalid slice.

    We detect this by noticing that the number of contours in the slice >= globs.NUM_CONTOURS_IN_INVALID_SLICE.

    Most brain slices have only 2 or 3 detectable contours.
    
    Change the number in globs.py, then run `pytest` and examine slices given by settings in
    tests/noise_vals.txt. Some valid slices have 6 or 7 contours.
    
    See NIFTI file (0, 0, 0, 151) for a valid slice with 9 contours. 9 seems like a good limit."""

    def __init__(self, num_contours):
        self.message = f'You attempted to compute the circumference of an invalid brain slice. Contours detected: {num_contours}\n' \
                       f'Likely noise or otherwise not a valid brain slice.'
        super().__init__(self.message)


class RemoveFromEmptyList(Exception):
    """Self-explanatory."""
    def __init__(self):
        self.message = f'You attempted to remove an image from an empty list of images.'
        super().__init__(self.message)


class RemoveFromListOfLengthOne(Exception):
    """If the list becomes empty, there's no image to render, which might cause an `IndexError`."""
    def __init__(self):
        self.message = f'You attempted to remove an image from a list of size 1 (i.e., the list would become empty after the delete).'
        super().__init__(self.message)


class RemoveAtInvalidIndex(Exception):
    """The error message accounts for the user seeing a 1-indexed list."""
    def __init__(self, index: int):
        self.message = f'You attempted to remove an image at index {index + 1}, which doesn\'t exist in the list of images.'
        super().__init__(self.message)


class UnexpectedNegativeNum(Exception):
    def __init__(self):
        self.message = f''
        super().__init__(self.message)

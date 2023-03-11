"""Custom image processing exceptions."""


# TODO: Make __init__ accept theta_x, theta_y, theta_z, slice_num as parameters to display those to the user?
# Probably not necessary because those will be displayed in the GUI.
class ComputeCircumferenceOfNoise(Exception):
    """User attempted to compute circumference of a slice that's just noise.

    We detect this by noticing that the number of contours in the slice > 9.

    Most brain slices have only 2 or 3 detectable contours.
    
    Change the number in imgproc_helpers, then run `pytest` and examine slices given by settings in tests/noise_vals.txt. Some valid slices have 6 or 7 contours.
    
    See NIFTI_PATH (0, 0, 0, 151) for a valid slice with 9 contours. 9 seems like a good limit."""

    def __init__(self):
        self.message = f'You attempted to compute the circumference of a slice that is just noise and not an actual brain slice (contours detected >= 10).'
        super().__init__(self.message)

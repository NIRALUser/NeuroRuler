"""Defines the `MRIImage` and `MRIImageList` classes."""

import _collections_abc
from typing import Union
import pathlib
import src.utils.exceptions as exceptions
import SimpleITK as sitk
import numpy as np

READER = sitk.ImageFileReader()


def degrees_to_radians(degrees: Union[int, float]) -> float:
    return degrees * np.pi / 180

class MRIImage:
    """Fields
    ------
    
    `base_img: sitk.Image`
        - Get

    `euler_3d_transform: sitk.Euler3DTransform`
        - Center of rotation set during initialization
        - Rotation parameters modified by calling theta setters

    `rotated_slice: sitk.Image`
        - Get
        - Created during initialization
        - Updated by `resample()`

    `path: pathlib.Path`
        - Get, set (should never be called, just make a new `MRIImage`)

    `theta_x: int`
        - In degrees
        - Get, set

    `theta_y: int`
        - In degrees
        - Get, set

    `theta_z: int`
        - In degrees
        - Get, set

    `slice_z: int`
        - Get, set"""
    base_img: sitk.Image
    """This is never mutated unless `set_path` is called.
    
    Of course, possible to access this field directly to modify it, but don't do that."""
    euler_3d_transform: sitk.Euler3DTransform
    rotated_slice: sitk.Image
    """`resample` applies the transform and sets this field."""
    path: pathlib.Path
    theta_x: int
    theta_y: int
    theta_z: int
    slice_z: int

    def __init__(self, path: pathlib.Path, theta_x: int=0, theta_y: int=0, theta_z: int=0, slice_z: int=0):
        """Sets the `base_img` field to be the result of using `sitk` to read `path`.
        
        Initializes a unique `Euler3DTransform` with center and rotation fields.

        Initializes `rotated_slice` to be the the result of resampling with the rotation and slice values."""
        self.path = path
        self.theta_x = theta_x
        self.theta_y = theta_y
        self.theta_z = theta_z
        self.slice_z = slice_z
        READER.SetFileName(str(path))
        self.base_img = READER.Execute()
        self.euler_3d_transform = sitk.Euler3DTransform()
        # TODO: This could be the wrong center
        self.euler_3d_transform.SetCenter(self.base_img.TransformContinuousIndexToPhysicalPoint([((dimension - 1) / 2.0) for dimension in self.base_img.GetSize()]))
        self.euler_3d_transform.SetRotation(degrees_to_radians(theta_x), degrees_to_radians(theta_y), degrees_to_radians(theta_z))
        self.rotated_slice = sitk.Resample(self.base_img, self.euler_3d_transform)[:, :, slice_z]

    def __repr__(self):
        """Prints only the necessary information to identify an `MRIImage`.
        
        That is, ignores `base_img`, `euler_3d_transform`, and `rotated_slice` since those are determined by `path` and rotation and slice values.
        
        But also, those fields can't be represented as `str`."""
        return f'MRIImage(\'{self.path}\', {self.theta_x}, {self.theta_y}, {self.theta_z}, {self.slice_z})'

    # == and != will check reference equality like normal. Use .equals() for deep equality.
    # def __eq__(self, other):
    #     return self.path == other.path and self.theta_x == other.theta_x and self.theta_y == other.theta_y and self.theta_z == other.theta_z and self.slice_z == other.slice_z

    def equals(self, other) -> bool:
        """Ignores `img` and `rotated_slice` fields. If the conditions checked are true, then `img` and `rotated_slice` are the same.
        
        Warning: Will return `True` for two `MRIImages` that have the same fields but different `rotated_slice` because they were last `resample`d with different fields.
        
        Could `resample` in this method to avoid that issue, but that seems inefficient."""
        return self.path == other.path and self.euler_3d_transform.GetCenter() == other.euler_3d_transform.GetCenter() and self.theta_x == other.theta_x and self.theta_y == other.theta_y and self.theta_z == other.theta_z and self.slice_z == other.slice_z

    def deepcopy(self):
        return MRIImage(self.path, self.theta_x, self.theta_y, self.theta_z, self.slice_z)
    
    def get_base_img(self) -> sitk.Image:
        return self.base_img

    def get_rotated_slice(self) -> sitk.Image:
        return self.rotated_slice

    def get_dimensions(self):
        return self.base_img.GetSize()

    def get_path(self) -> pathlib.Path:
        return self.path

    def get_theta_x(self) -> int:
        return self.theta_x

    def get_theta_y(self) -> int:
        return self.theta_y

    def get_theta_z(self) -> int:
        return self.theta_z

    def get_slice_z(self) -> int:
        return self.slice_z

    # No set_img or set_euler_3d_transform functions. set_path does it.

    def set_path(self, path: pathlib.Path):
        """Honestly, this function should never be called. Just delete the old `MRIImage`, and construct a new one.
        
        Keeps the same `Euler3DTransform` but sets its center to the center of the new file.
        
        Sets rotation values and slice num to 0."""
        self.path = path
        READER.SetFileName(str(path))
        self.base_img = READER.Execute()
        # TODO: This could be the wrong center
        self.euler_3d_transform.SetCenter(self.base_img.TransformContinuousIndexToPhysicalPoint([((dimension - 1) / 2.0) for dimension in self.base_img.GetSize()]))
        self.euler_3d_transform.SetRotation(0, 0, 0)
        self.theta_x = 0
        self.theta_y = 0
        self.theta_z = 0
        self.slice_z = 0

    def set_theta_x(self, theta_x: int):
        """Sets `theta_x` field in the `MRIImage` and in the `euler_3d_transform` object.
        
        Does not `resample`."""
        self.theta_x = theta_x
        self.euler_3d_transform.SetRotation(degrees_to_radians(theta_x), degrees_to_radians(self.theta_y), degrees_to_radians(self.theta_z))

    def set_theta_y(self, theta_y: int):
        """Sets `theta_y` field in the `MRIImage` and in the `euler_3d_transform` object.
        
        Does not `resample`."""
        self.theta_y = theta_y
        self.euler_3d_transform.SetRotation(degrees_to_radians(self.theta_x), degrees_to_radians(theta_y), degrees_to_radians(self.theta_z))

    def set_theta_z(self, theta_z: int):
        """Sets `theta_z` field in the `MRIImage` and in the `euler_3d_transform` object.
        
        Does not `resample`."""
        self.theta_z = theta_z
        self.euler_3d_transform.SetRotation(degrees_to_radians(self.theta_x), degrees_to_radians(self.theta_y), degrees_to_radians(theta_z))

    def set_slice_z(self, slice_z: int):
        """Sets `slice_z` field in the `MRIImage`.
        
        Does not `resample`."""
        self.slice_z = slice_z
    
    def resample(self) -> None:
        """Sets `rotated_slice` to the result of resampling with this instance's rotation and slice values.
        
        Could resample after setter methods, but that's inefficient."""
        self.rotated_slice = sitk.Resample(self.base_img, self.euler_3d_transform)[:, :, self.slice_z]


# Credit: https://github.com/python/cpython/blob/208a7e957b812ad3b3733791845447677a704f3e/Lib/collections/__init__.py#L1174
class MRIImageList(_collections_abc.MutableSequence):
    """There should only be a single instance of `MRIImageList`. It modifies global variables.
    
    Not enforced, but don't make more than one instance."""
    # Commented out because this syntax doesn't work on older versions of Python
    # images: list[MRIImage]
    index: int = 0

    def __init__(self, init_list=None):
        """Parameters
        ---------
        images: `list[MRIImage]` | `None` (no arg)"""
        self.images = []
        if init_list is not None:
            if type(init_list) == type(self.images):
                self.images[:] = init_list
            elif isinstance(init_list, MRIImageList):
                self.images[:] = init_list.images[:]
            else:
                self.images = init_list

    def __repr__(self):
        return repr(self.images)

    def __len__(self) -> int:
        return len(self.images)

    def __getitem__(self, i):
        """If `i` is `int`, returns a reference to `self.images[i]`.
        
        If `i` is `slice`, returns a deep copy of the `ImageList`, but the individual elements are shallow copies (i.e., references are the same).
        
        This is the [same behavior as in normal Python](https://stackoverflow.com/questions/19068707/does-a-slicing-operation-give-me-a-deep-or-shallow-copy)."""
        if isinstance(i, slice):
            return self.__class__(self.images[i])
        else:
            return self.images[i]
    
    # TODO: Make GUI comply with the docstring
    def __delitem__(self, i: int):
        """Does not advance `index` if `i == index`. The GUI should refresh the image after a delete.
        
        This edge case should not be handled here. TODO"""
        del self.images[i]
    
    def __setitem__(self, i: int, image: MRIImage):
        """Doesn't modify `index`."""
        self.images[i] = image

    def __contains__(self, image: MRIImage) -> bool:
        return image in self.images

    def insert(self, i: int, image: MRIImage):
        """Doesn't modify `index`."""
        self.images.insert(i, image)
        
    def append(self, image: MRIImage):
        self.images.append(image)

    def extend(self, other):
        """Parameters
        ----------
        other: `ImageList` | `list[Image]`"""
        if isinstance(other, MRIImageList):
            self.images.extend(other.images)
        else:
            self.images.extend(other)

    def clear(self):
        self.images.clear()

    def pop(self, i=-1) -> MRIImage:
        """Default parameter -1 (i.e., pop last element)."""
        return self.images.pop(i)

    def next(self):
        """Advance `index` by 1.
        
        If `index` is the last index, wraps to 0.
        
        If the length is of length 0, then there will be a `ZeroDivisionError`.
        
        TODO: Disable the buttons in the GUI when the list is of length 0 or 1."""
        self.index = (self.index + 1) % len(self.images)
        # TODO: This needs to be handled in the GUI instead. Disable the next and previous buttons when len(list) is 0 or 1.
        if len(self) == 1:
            self.index = 0
            print("Calling next() when the list has one element doesn't do anything.")

    def previous(self):
        """Decrement `index` by 1.
        
        If `index` is 0, wraps to the last index.

        If the length is of length 0, then there will be a `ZeroDivisionError`.
        
        TODO: Disable the buttons in the GUI when the list is of length 0 or 1."""
        self.index = (self.index - 1) % len(self.images)
        # TODO: This needs to be handled in the GUI instead. Disable the next and previous buttons when len(list) is 0 or 1.
        if len(self) == 1:
            self.index = 0
            print("Calling previous() when the list has one element doesn't do anything.")

    def get_curr_mri_image(self) -> MRIImage:
        """Return a reference to the `MRIImage` at the current `index`."""
        return self.images[self.index]

    def get_index(self) -> int:
        return self.index

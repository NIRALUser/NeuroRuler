"""Defines the `MRIImage` and `MRIImageList` classes.

See https://stackoverflow.com/questions/2627002/whats-the-pythonic-way-to-use-getters-and-setters.

And https://realpython.com/python-property/."""

import _collections_abc
from typing import Union
import pathlib
import src.utils.exceptions as exceptions
import SimpleITK as sitk
import numpy as np
import warnings
import functools

READER = sitk.ImageFileReader()
ROTATION_MIN: int = 0
"""Degrees"""
ROTATION_MAX: int = 180
"""Degrees"""

# Can't import this from globs due to circular import
# Source: https://stackoverflow.com/questions/2536307/decorators-in-the-python-standard-lib-deprecated-specifically
def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning)  # turn off filter
        warnings.warn("Call to deprecated function {}.".format(func.__name__),
                      category=DeprecationWarning,
                      stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning)  # reset filter
        return func(*args, **kwargs)

    return new_func

class MRIImage:
    """Fields
    ------
    
    `base_img: sitk.Image`
        - Get
        - Never mutate this

    `euler_3d_transform: sitk.Euler3DTransform`
        - Center of rotation set during initialization
        - Rotation parameters modified by calling theta setters

    `rotated_slice: sitk.Image`
        - Get
        - Created during initialization
        - Updated by `resample()`

    `path: pathlib.Path`
        - Get

    `theta_x: int, theta_y: int, theta_z: intt`
        - In degrees
        - Get, set

    `slice_z: int`
        - Get, set"""

    def __init__(self, path: pathlib.Path, theta_x: int=0, theta_y: int=0, theta_z: int=0, slice_z: int=0):
        """Sets the `base_img` field to be the result of using `sitk` to read `path`.
        
        Initializes a unique `Euler3DTransform` with center and rotation fields.

        Initializes `rotated_slice` to be the the result of resampling with the rotation and slice values."""
        self._path = path
        self._theta_x = theta_x
        self._theta_y = theta_y
        self._theta_z = theta_z
        self._slice_z = slice_z
        READER.SetFileName(str(path))
        self._base_img = READER.Execute()
        self._euler_3d_transform = sitk.Euler3DTransform()
        # TODO: This could be the wrong center
        self._euler_3d_transform.SetCenter(self._base_img.TransformContinuousIndexToPhysicalPoint([((dimension - 1) / 2.0) for dimension in self._base_img.GetSize()]))
        self._euler_3d_transform.SetRotation(degrees_to_radians(theta_x), degrees_to_radians(theta_y), degrees_to_radians(theta_z))
        # Sets self._rotated_slice
        self.resample()

    def __repr__(self):
        """Prints only the necessary information to identify an `MRIImage`.
        
        That is, ignores `base_img`, `euler_3d_transform`, and `rotated_slice` since those are determined by `path` and rotation and slice values.
        
        But also, those fields can't be represented as `str`."""
        return f'MRIImage(\'{self._path}\', {self._theta_x}, {self._theta_y}, {self._theta_z}, {self._slice_z})'

    # == and != will check reference equality like normal. Use .equals() for deep equality.
    # def __eq__(self, other):
    #     return self.path == other.path and self.theta_x == other.theta_x and self.theta_y == other.theta_y and self.theta_z == other.theta_z and self.slice_z == other.slice_z

    def equals(self, other) -> bool:
        """Ignores `img` and `rotated_slice` fields. If the conditions checked are true, then `img` and `rotated_slice` are the same.
        
        Warning: Will return `True` for two `MRIImages` that have the same fields but different `rotated_slice` because they were last `resample`d with different fields.
        
        Could `resample` in this method to avoid that issue, but that seems inefficient."""
        return self._path == other.path and self._euler_3d_transform.GetCenter() == other.euler_3d_transform.GetCenter() and self._theta_x == other.theta_x and self._theta_y == other.theta_y and self._theta_z == other.theta_z and self._slice_z == other.slice_z

    def deepcopy(self):
        return MRIImage(self._path, self._theta_x, self._theta_y, self._theta_z, self._slice_z)
    
    @property
    def base_img(self) -> sitk.Image:
        return self._base_img

    @property
    def rotated_slice(self) -> sitk.Image:
        return self._rotated_slice

    def get_dimensions(self):
        return self._base_img.GetSize()

    @property
    def path(self) -> pathlib.Path:
        return self._path

    @property
    def theta_x(self) -> int:
        return self._theta_x

    @property
    def theta_y(self) -> int:
        return self._theta_y

    @property
    def theta_z(self) -> int:
        return self._theta_z

    @property
    def slice_z(self) -> int:
        return self._slice_z

    # No set_img or set_euler_3d_transform functions. set_path does it.

    @deprecated
    @path.setter
    def set_path(self, path: pathlib.Path):
        """Honestly, this function should never be called. Just delete the old `MRIImage`, and construct a new one.
        
        Keeps the same `Euler3DTransform` but sets its center to the center of the new file.
        
        Sets rotation values and slice num to 0 and `resample`s."""
        self._path = path
        READER.SetFileName(str(path))
        self._base_img = READER.Execute()
        # TODO: This could be the wrong center
        self._euler_3d_transform.SetCenter(self.base_img.TransformContinuousIndexToPhysicalPoint([((dimension - 1) / 2.0) for dimension in self.base_img.GetSize()]))
        self._euler_3d_transform.SetRotation(0, 0, 0)
        self._theta_x = 0
        self._theta_y = 0
        self._theta_z = 0
        self._slice_z = 0
        self.resample()

    @theta_x.setter
    def theta_x(self, theta_x: int):
        """Sets `theta_x` field in the `MRIImage` and in the `euler_3d_transform` object.
        
        Does not `resample`."""
        self._theta_x = theta_x
        self._euler_3d_transform.SetRotation(degrees_to_radians(theta_x), degrees_to_radians(self._theta_y), degrees_to_radians(self._theta_z))

    @theta_y.setter
    def theta_y(self, theta_y: int):
        """Sets `theta_y` field in the `MRIImage` and in the `euler_3d_transform` object.
        
        Does not `resample`."""
        self._theta_y = theta_y
        self._euler_3d_transform.SetRotation(degrees_to_radians(self._theta_x), degrees_to_radians(theta_y), degrees_to_radians(self._theta_z))

    @theta_z.setter
    def theta_z(self, theta_z: int):
        """Sets `theta_z` field in the `MRIImage` and in the `euler_3d_transform` object.
        
        Does not `resample`."""
        self._theta_z = theta_z
        self._euler_3d_transform.SetRotation(degrees_to_radians(self._theta_x), degrees_to_radians(self._theta_y), degrees_to_radians(theta_z))

    @slice_z.setter
    def slice_z(self, slice_z: int):
        """Sets `slice_z` field in the `MRIImage`.
        
        Does not `resample`."""
        self._slice_z = slice_z

    def resample(self) -> None:
        """Sets `rotated_slice` to the result of resampling with this instance's rotation and slice values."""
        self._rotated_slice = sitk.Resample(self._base_img, self._euler_3d_transform)[:, :, self._slice_z]


# Credit: https://github.com/python/cpython/blob/208a7e957b812ad3b3733791845447677a704f3e/Lib/collections/__init__.py#L1174
class MRIImageList(_collections_abc.MutableSequence):
    """There should only be a single instance of `MRIImageList` since there's a global MRIImageList.
    
    Not enforced, but don't make more than one instance.
    
    Fields
    ------
    images: list[MRIImage]
        - Get, set (but really should never call the setter)
    
    index: int
        - Get, set

        - Index of current MRIImage"""

    _index: int = 0

    def __init__(self, init_list=None):
        """Parameters
        ---------
        images: `list[MRIImage]` | `None` (no arg)"""
        self._images = []
        if init_list is not None:
            if type(init_list) == type(self._images):
                self._images[:] = init_list
            elif isinstance(init_list, MRIImageList):
                self._images[:] = init_list.images[:]
            else:
                self._images = init_list

    @property
    def images(self) -> list[MRIImage]:
        return self._images

    @property
    def index(self) -> int:
        return self._index

    @images.setter
    def images(self, images: list[MRIImage]) -> None:
        self._images = images

    @index.setter
    def index(self, index: int) -> None:
        self._index = index

    def __repr__(self) -> str:
        return repr(self._images)

    def __len__(self) -> int:
        return len(self._images)

    def __getitem__(self, i):
        """If `i` is `int`, returns a reference to `self.images[i]`.
        
        If `i` is `slice`, returns a deep copy of the `ImageList`, but the individual elements are shallow copies (i.e., references are the same).
        
        This is the [same behavior as in normal Python](https://stackoverflow.com/questions/19068707/does-a-slicing-operation-give-me-a-deep-or-shallow-copy)."""
        if isinstance(i, slice):
            return self.__class__(self._images[i])
        else:
            return self._images[i]
    
    # TODO: Make GUI comply with the docstring
    def __delitem__(self, i: int):
        """If `i == index`, the GUI should re-render the image afterward.
        
        TODO: GUI should prevent delete when there's only one image."""
        if len(self) == 0:
            raise exceptions.RemoveFromEmptyList()
        if len(self) == 1:
            raise exceptions.RemoveFromListOfLengthOne()
        del self._images[i]
    
    def __setitem__(self, i: int, image: MRIImage):
        """If `i == index`, the GUI should re-render the image."""
        self._images[i] = image

    def __contains__(self, image: MRIImage) -> bool:
        return image in self._images

    def insert(self, i: int, image: MRIImage):
        """If `i == index`, GUI should re-render the image."""
        self._images.insert(i, image)
        
    def append(self, image: MRIImage):
        self._images.append(image)

    def extend(self, other):
        """Parameters
        ----------
        other: `ImageList` | `list[Image]`"""
        if isinstance(other, MRIImageList):
            self._images.extend(other._images)
        else:
            self._images.extend(other)

    def clear(self):
        """If this is called, reset GUI to initial state (i.e., everything disabled)."""
        self._images.clear()
        self._index = 0

    def pop(self, i=-1) -> MRIImage:
        """Default parameter -1 (i.e., pop last element).
        
        If `i == index`, GUI should re-render image afterward.
        
        TODO: GUI should prevent pop when there's only one image."""
        if len(self) == 0:
            raise exceptions.RemoveFromEmptyList()
        if len(self) == 1:
            raise exceptions.RemoveFromListOfLengthOne()
        return self._images.pop(i)

    def next(self):
        """Advance `index` by 1.
        
        If `index` is the last index, wraps to 0.
        
        If the length is of length 0, then there will be a `ZeroDivisionError`.
        
        TODO: Disable the buttons in the GUI when the list is of length 0 or 1."""
        self._index = (self._index + 1) % len(self._images)
        # TODO: This needs to be handled in the GUI instead. Disable the next and previous buttons when len(list) is 0 or 1.
        if len(self) == 1:
            self._index = 0
            print("Calling next() when the list has one element doesn't do anything.")

    def previous(self):
        """Decrement `index` by 1.
        
        If `index` is 0, wraps to the last index.

        If the length is of length 0, then there will be a `ZeroDivisionError`.
        
        TODO: Disable the buttons in the GUI when the list is of length 0 or 1."""
        self._index = (self._index - 1) % len(self._images)
        # TODO: This needs to be handled in the GUI instead. Disable the next and previous buttons when len(list) is 0 or 1.
        if len(self) == 1:
            self._index = 0
            print("Calling previous() when the list has one element doesn't do anything.")

def degrees_to_radians(degrees: Union[int, float]) -> float:
    return degrees * np.pi / 180

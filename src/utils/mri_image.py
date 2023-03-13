"""Defines the Image and ImageList classes.

Probably should change the name, might be confusing."""

import _collections_abc
from typing import Union
import pathlib
import src.utils.exceptions as exceptions

class MRIImage:
    # TODO: Change this to Path
    path: pathlib.Path
    theta_x: int
    theta_y: int
    theta_z: int
    slice_z: int

    def __init__(self, path: pathlib.Path, theta_x: int=0, theta_y: int=0, theta_z: int=0, slice_z: int=0):
        self.path = path
        self.theta_x = theta_x
        self.theta_y = theta_y
        self.theta_z = theta_z
        self.slice_z = slice_z

    def __repr__(self):
        return f'Image(\'{self.path}\', {self.theta_x}, {self.theta_y}, {self.theta_z}, {self.slice_z})'

    # == and != will check reference equality like normal. Use .equals() for deep equality.
    # def __eq__(self, other):
    #     return self.path == other.path and self.theta_x == other.theta_x and self.theta_y == other.theta_y and self.theta_z == other.theta_z and self.slice_z == other.slice_z

    def equals(self, other) -> bool:
        return self.path == other.path and self.theta_x == other.theta_x and self.theta_y == other.theta_y and self.theta_z == other.theta_z and self.slice_z == other.slice_z

    def deepcopy(self):
        return MRIImage(self.path, self.theta_x, self.theta_y, self.theta_z, self.slice_z)

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

    def set_path(self, path: pathlib.Path):
        self.path = path

    def set_theta_x(self, theta_x: int):
        self.theta_x = theta_x

    def set_theta_y(self, theta_y: int):
        self.theta_y = theta_y

    def set_theta_z(self, theta_z: int):
        self.theta_z = theta_z

    def set_slice_z(self, slice_z: int):
        self.slice_z = slice_z
    

# Credit: https://github.com/python/cpython/blob/208a7e957b812ad3b3733791845447677a704f3e/Lib/collections/__init__.py#L1174
class MRIImageList(_collections_abc.MutableSequence):
    images: list[MRIImage]
    index: int

    def __init__(self, init_list=None):
        """Parameters
        ---------
        images: `list[Image]` | `None` (no arg)"""
        self.images = []
        if init_list is not None:
            if type(init_list) == type(self.images):
                self.images[:] = init_list
            elif isinstance(init_list, MRIImageList):
                self.images[:] = init_list.images[:]
            else:
                self.images = list(init_list)

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
    
    def __delitem__(self, i: int):
        """First advances `index` if `i == index`."""
        if i == self.index:
            self.next()
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
        
        If `index` is the last index, wraps to 0."""
        self.index = (self.index + 1) % len(self.images)

    def previous(self):
        """Decrement `index` by 1.
        
        If `index` is 0, wraps to the last index."""
        self.index = (self.index - 1) % len(self.images)

"""Defines the `MRIImage` and `MRIImageList` classes.

See https://stackoverflow.com/questions/2627002/whats-the-pythonic-way-to-use-getters-and-setters.

And https://realpython.com/python-property/.

See https://peps.python.org/pep-0258/#attribute-docstrings for how to document classes
to auto-generate documentation."""

import _collections_abc
from pathlib import Path
from typing import Union

import SimpleITK as sitk

import src.utils.exceptions as exceptions
import src.utils.settings as settings
from src.utils.constants import degrees_to_radians, deprecated, NIFTI_UNITS

# Can't import this from globs due to circular import
READER: sitk.ImageFileReader = sitk.ImageFileReader()
"""Global `sitk.ImageFileReader` within the mri_image.py file.

DO NOT use this for a new MRIImage while it's currently being used in __init__ for another MRIImage."""
EULER_3D_TRANSFORM: sitk.Euler3DTransform = sitk.Euler3DTransform()
"""Global `sitk.Euler3DTransform` within the mri_image.py file.

Set its center and rotation before resampling."""
MESSAGE_TO_SHOW_IF_UNITS_NOT_FOUND: str = "units not found in metadata"


class MRIImage:
    """Represents an MRI image slice.

    Wraps an entire 3D MRI image, and the attributes identify a specific 2D slice that is generated by
    `resample()`.

    This allows the GUI to remember settings for different MRI images."""

    def __init__(
        self,
        path: Path,
        theta_x: int = 0,
        theta_y: int = 0,
        theta_z: int = 0,
        slice_num: int = 0,
    ) -> None:
        self._path = path
        """Path to MRI image. Get, set defined, but set should never be used."""
        READER.SetFileName(str(path))
        self._base_img = READER.Execute()
        """The base image, which should never be mutated. Get."""
        self._center = self._base_img.TransformContinuousIndexToPhysicalPoint(
            [((dimension - 1) / 2.0) for dimension in self._base_img.GetSize()]
        )
        """Center of rotation.
        
        `EULER_3D_TRANSFORM`'s center is set to this in `resample()`.
        
        Doesn't have to be encapsulated since it can be generated from `base_img`, but this prevents
        recalculation of it."""
        self._units = (
            NIFTI_UNITS[READER.GetMetaData("xyzt_units")]
            if "xyzt_units" in READER.GetMetaDataKeys()
            else MESSAGE_TO_SHOW_IF_UNITS_NOT_FOUND
        )
        """Units of the base image from its metadata.
        
        TODO: Doesn't work for NRRD images since it doesn't have a units key. How to get NRRD's units?"""
        self._theta_x = theta_x
        """X rotation value in degrees. Get, set."""
        self._theta_y = theta_y
        """Y rotation value in degrees. Get, set."""
        self._theta_z = theta_z
        """Z rotation value in degrees. Get, set."""
        self._slice_num = slice_num
        """Slice value. Get, set."""
        self._metadata: dict[str, str] = dict()
        """Metadata from `sitk`."""
        for key in READER.GetMetaDataKeys():
            self._metadata[key] = READER.GetMetaData(key)

    def __repr__(self) -> str:
        """Prints only the necessary information to identify an `MRIImage`.

        That is, ignores `base_img` since it's determined by `path` and rotation and slice values.

        Ignores `center` since it's determined by `base_img`.

        :return: str representation of an MRIImage
        :rtype: str"""
        return f"MRIImage('{self._path}', {self._theta_x}, {self._theta_y}, {self._theta_z}, {self._slice_num})"

    @property
    def path(self) -> Path:
        return self._path

    @property
    def base_img(self) -> sitk.Image:
        return self._base_img

    @property
    def center(self) -> tuple:
        return self._center

    @property
    def units(self) -> str:
        return self._units

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
    def slice_num(self) -> int:
        return self._slice_num

    @property
    def metadata(self) -> dict[str, str]:
        return self._metadata

    @path.setter
    def path(self, path: Path) -> None:
        """Honestly, this setter should never be called. Just delete the old `MRIImage`, and construct a new one.

        Sets center. Sets rotation values and slice num to 0.

        :rtype: None"""
        self._path = path
        READER.SetFileName(str(path))
        self._base_img = READER.Execute()
        self._center = self._base_img.TransformContinuousIndexToPhysicalPoint(
            [((dimension - 1) / 2.0) for dimension in self._base_img.GetSize()]
        )
        self._theta_x = 0
        self._theta_y = 0
        self._theta_z = 0
        self._slice_num = 0

    @theta_x.setter
    def theta_x(self, theta_x: int) -> None:
        self._theta_x = theta_x

    @theta_y.setter
    def theta_y(self, theta_y: int) -> None:
        self._theta_y = theta_y

    @theta_z.setter
    def theta_z(self, theta_z: int) -> None:
        self._theta_z = theta_z

    @slice_num.setter
    def slice_num(self, slice_num: int) -> None:
        self._slice_num = slice_num

    def get_size(self) -> tuple:
        """Returns dimensions of the base image.

        :return: Dimensions
        :rtype: tuple"""
        return self._base_img.GetSize()

    def equals(self, other) -> bool:
        """Checks for deep equality. Ignores `base_img` field.
        If the conditions checked are true, then `base_img` is the same.

        :param other:
        :type other: MRIImage
        :return: True if deeply equal, else False
        :rtype: bool"""
        return (
            self._path == other.path
            and self._center == other.center
            and self._theta_x == other.theta_x
            and self._theta_y == other.theta_y
            and self._theta_z == other.theta_z
            and self._slice_num == other.slice_num
        )

    # TODO: deprecated because deepcopy creates a file with the same path, which shouldn't happen.
    # However, some unit tests use deepcopy
    @deprecated
    def deepcopy(self) -> "MRIImage":
        """Return a deep copy.

        Deprecated because duplicate paths should not be possible.

        :return: Deep copy
        :rtype: MRIImage"""
        return MRIImage(
            self._path, self._theta_x, self._theta_y, self._theta_z, self._slice_num
        )

    # TODO: Should this apply smoothing first (and remove it from imgproc.py), then return to GUI for display?
    def resample(self) -> sitk.Image:
        """Returns the rotated slice that's the result of resampling with this instance's rotation and slice values.

        The slice is also smoothed if `settings.SMOOTH_BEFORE_RENDERING` is True.

        :return: Rotated slice that's also smoothed if settings.SMOOTH_BEFORE_RENDERING
        :rtype: sitk.Image"""
        EULER_3D_TRANSFORM.SetCenter(self.center)
        EULER_3D_TRANSFORM.SetRotation(
            degrees_to_radians(self.theta_x),
            degrees_to_radians(self.theta_y),
            degrees_to_radians(self.theta_z),
        )
        rotated_slice: sitk.Image = sitk.Resample(self._base_img, EULER_3D_TRANSFORM)[
            :, :, self._slice_num
        ]
        if settings.SMOOTH_BEFORE_RENDERING:
            smooth_slice: sitk.Image = (
                sitk.GradientAnisotropicDiffusionImageFilter().Execute(
                    sitk.Cast(rotated_slice, sitk.sitkFloat64)
                )
            )
            if settings.DEBUG:
                print("resample() returned a smoothed slice")
            return smooth_slice
        return rotated_slice

    # TODO: Should this apply smoothing first (and remove it from imgproc.py), then return to GUI for display?
    def resample_hardcoded(
        self, theta_x: int = 0, theta_y: int = 0, theta_z: int = 0, slice_num: int = 0
    ) -> sitk.Image:
        """Return the rotated slice with hardcoded settings (i.e., not the instance's settings).
        Mostly used in test functions. Should not be used in actual program.

        The slice is also smoothed if `settings.SMOOTH_BEFORE_RENDERING` is True.

        Calls `resample()`. Does not mutate the instance's attributes (i.e.,
        temporarily modifies them but sets them back to original values).

        :param theta_x: X rotation value in degrees, defaults to 0
        :type theta_x: int
        :param theta_y: Y rotation value in degrees, defaults to 0
        :type theta_y: int
        :param theta_z: Z rotation value in degrees, defaults to 0
        :type theta_z: int
        :param slice_num: Slice value, defaults to 0
        :type slice_num: int
        :return: Rotated slice resulting from resampling the base image with the hardcoded values
        :rtype: sitk.Image"""
        theta_x_copy, theta_y_copy, theta_z_copy, slice_num_copy = (
            self._theta_x,
            self._theta_y,
            self._theta_z,
            self._slice_num,
        )
        self._theta_x, self._theta_y, self._theta_z, self._slice_num = (
            theta_x,
            theta_y,
            theta_z,
            slice_num,
        )
        rv: sitk.Image = self.resample()
        self._theta_x, self._theta_y, self._theta_z, self._slice_num = (
            theta_x_copy,
            theta_y_copy,
            theta_z_copy,
            slice_num_copy,
        )
        return rv


# Credit: https://github.com/python/cpython/blob/208a7e957b812ad3b3733791845447677a704f3e/Lib/collections/__init__.py#L1174
# Pretty much copy-pasted with some modifications
class MRIImageList(_collections_abc.MutableSequence):
    """Wraps a list[MRIImage] and a single index. Provides methods for moving the index and modifying the list.

    There should only be a single instance of `MRIImageList` since there's a global MRIImageList.

    Not enforced, but don't make more than one instance.

    Wraps a set of image paths that is updated on insert & remove operations.
    Duplicate paths are not allowed.

    The methods involving `_paths` are not unit tested but work in the GUI.
    Specifically, the constructor called on `list[MRIImage]` works as expected.
    Also `.extend()` and `__delitem__()`.

    Does not handle edge cases such as removing from empty list or list of length 1
    (no image to display) since that belongs in the GUI."""

    def __init__(
        self, init_list: Union[list[MRIImage], "MRIImageList", None] = None
    ) -> None:
        self._images: list[MRIImage] = []
        """List of `MRIImage`. Get, set (but really should never set)."""
        self._index: int = 0
        """Current index. Get, set."""
        self._paths: set[Path] = set()
        """Set of `Path`s of `MRIImage`s. Get."""
        if init_list is not None:
            if type(init_list) == type(self._images):
                self._images[:] = init_list
                for image in init_list:
                    self._paths.add(image.path)
            elif isinstance(init_list, MRIImageList):
                # See https://stackoverflow.com/questions/36317652/whats-the-meaning-of-x-y
                # For explanation of x[:] = y
                self._images[:] = init_list.images[:]
                # set() creates a deep copy and also doesn't create a set of sets like {{1}}
                self._paths = set(init_list.paths)
            else:
                self._images = init_list

    @property
    def images(self) -> list[MRIImage]:
        return self._images

    @property
    def index(self) -> int:
        return self._index

    @property
    def paths(self) -> set[Path]:
        return self._paths

    @images.setter
    def images(self, images: list[MRIImage]) -> None:
        self._images = images
        self._paths.clear()
        for image in images:
            self._paths.add(image.path)

    @index.setter
    def index(self, index: int) -> None:
        self._index = index

    def __repr__(self) -> str:
        """Return `str` representation of `MRIImageList`."""
        return repr(self._images)

    def __len__(self) -> int:
        """Return length of images."""
        return len(self._images)

    def __getitem__(self, i: Union[int, slice]) -> Union[MRIImage, "MRIImageList"]:
        """If `i` is `int`, returns a reference to `self.images[i]`.

        If `i` is `slice`, returns a clone of the `ImageList` (different object id),
        but the individual elements are shallow copies (i.e., references are the same).

        This is the [same behavior as in normal Python](https://stackoverflow.com/questions/19068707/does-a-slicing-operation-give-me-a-deep-or-shallow-copy).

        :param i:
        :type i: int or slice
        :return: Single MRIImage or MRIImageList
        :rtype: MRIImage or MRIImageList"""
        if isinstance(i, slice):
            return self.__class__(self._images[i])
        else:
            return self._images[i]

    # TODO: Make GUI comply with the docstring
    def __delitem__(self, i: int) -> None:
        """TODO: GUI should prevent delete when there's only one image.

        If `i == index`, the GUI should re-render the image afterward.

        :param i:
        :type i: int"""
        self._paths.remove(self._images[i].path)
        del self._images[i]

    # TODO: If i == index, the GUI should re-render the image
    def __setitem__(self, i: int, image: MRIImage) -> None:
        """TODO: If i == index, the GUI should re-render the image

        :param i: index
        :type i: int
        :raise exceptions.DuplicateFilepathsInMRIImageList if image.path in self._paths. But won't raise exception if setting image to itself.
        """
        self._paths.remove(self._images[i].path)
        if image.path in self._paths:
            raise exceptions.DuplicateFilepathsInMRIImageList({image.path})
        self._paths.add(image.path)
        self._images[i] = image

    # TODO: Unit test this
    def __contains__(self, image: MRIImage) -> bool:
        """Internally, does not check `image in self._images`. Instead, checks `image.path in self._paths`.

        :param image:
        :type image: MRIImage"""
        return image.path in self._paths

    # TODO: If i == index, GUI should re-render the image
    def insert(self, i: int, image: MRIImage) -> None:
        """if `i == index`, GUI should re-render the image.

        :param i:
        :type i: MRIImage
        :raise: exceptions.DuplicateFilepathsInMRIImageList if image.path in self._paths
        """
        if image.path in self._paths:
            raise exceptions.DuplicateFilepathsInMRIImageList({image.path})
        self._paths.add(image.path)
        self._images.insert(i, image)

    def append(self, image: MRIImage) -> None:
        """:param image:
        :type image: MRIImage
        :raise: exceptions.DuplicateFilepathsInMRIImageList if image.path in self._paths
        """
        if image.path in self._paths:
            raise exceptions.DuplicateFilepathsInMRIImageList({image.path})
        self._paths.add(image.path)
        self._images.append(image)

    def extend(self, other: Union["MRIImageList", list[MRIImage]]) -> None:
        """Extend images list.

        If `other` is a list[MRIImage] that contains duplicate paths, the duplicates will be removed.

        :param other:
        :type other: list[MRIImage] or MRIImageList
        :raise: exceptionsDuplicateFilepathsInMRIImageList if there's intersection between the paths of self and other.
        """
        other_paths: set = (
            other.paths
            if isinstance(other, MRIImageList)
            else {image.path for image in other}
        )
        disjoint, union_or_intersect = combine_sets(self._paths, other_paths)
        if not disjoint:
            raise exceptions.DuplicateFilepathsInMRIImageList(union_or_intersect)
        self._paths = union_or_intersect
        self._images.extend(other._images if isinstance(other, MRIImageList) else other)

    def clear(self) -> None:
        """TODO: If this is called, reset GUI to initial state (i.e., everything disabled).

        Sets _index to 0."""
        self._images.clear()
        self._index = 0
        self._paths.clear()

    def pop(self, i: int = -1) -> MRIImage:
        """TODO: GUI should prevent `pop` when there's only one image.

        If `i == index`, GUI should re-render image afterward.

        :param i: Defaults to -1 (i.e., pop last element)
        :type i: int
        :return: Popped `MRIImage`
        :rtype: `MRIImage`"""
        self._paths.remove(self._images[i].path)
        return self._images.pop(i)

    def next(self) -> None:
        """Advance `index` by 1.

        If `index` is the last index, wraps to 0.

        If the length is of length 0, then there will be a `ZeroDivisionError`.

        TODO: Disable the buttons in the GUI when the list is of length 0 or 1."""
        self._index = (self._index + 1) % len(self._images)
        # TODO: This needs to be handled in the GUI instead. Disable the next and previous buttons when len(list) is 0 or 1.
        if len(self) == 1:
            self._index = 0
            print("Calling next() when the list has one element doesn't do anything.")

    def previous(self) -> None:
        """Decrement `index` by 1.

        If `index` is 0, wraps to the last index.

        If the length is of length 0, then there will be a `ZeroDivisionError`.

        TODO: Disable the buttons in the GUI when the list is of length 0 or 1."""
        self._index = (self._index - 1) % len(self._images)
        # TODO: This needs to be handled in the GUI instead. Disable the next and previous buttons when len(list) is 0 or 1.
        if len(self) == 1:
            self._index = 0
            print(
                "Calling previous() when the list has one element doesn't do anything."
            )


def combine_sets(x: set, y: set) -> tuple:
    """If no intersection between x and y, return (True, x ∪ y).
    Otherwise, return (False, x ∩ y).

    The `bool` of the tuple should be interpreted as "disjoint".

    Used to check for intersection between set[Path] in extend()
    Most of the time, there will not be intersection between sets of Paths.

    :param x:
    :type x: set[Path]
    :param y:
    :type y: set[Path]
    :return: (True, x ∪ y) if x and y are disjoint, else (False, x ∩ y)
    :rtype: tuple"""
    union: set = x.union(y)
    if len(union) != len(x) + len(y):
        return (False, x.intersection(y))
    return (True, union)

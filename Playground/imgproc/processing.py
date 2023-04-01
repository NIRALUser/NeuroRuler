import SimpleITK as sitk
import numpy as np
import matplotlib.pyplot as plt

OUTPUT_DIR = "out"
NRRD1_PATH = "ExampleData/BCP_Dataset_2month_T1w.nrrd"
NRRD2_PATH = "ExampleData/IBIS_Dataset_12month_T1w.nrrd"
NRRD3_PATH = "ExampleData/IBIS_Dataset_NotAligned_6month_T1w.nrrd"
NIFTI_PATH = "ExampleData/MicroBiome_1month_T1w.nii.gz"

x_rotation = 0
y_rotation = 0
z_rotation = 0
slice_num = 70


def main() -> None:
    reader = sitk.ImageFileReader()
    reader.SetFileName(NIFTI_PATH)
    image = reader.Execute()
    # rotated_image = apply_rotations(image, 0, 0, 30)
    # current_slice = rotated_image[:, :, slice_num]
    # show_current_slice(current_slice)
    current_slice = image[:, :, slice_num]
    process_slice(current_slice)


# https://slicer.readthedocs.io/en/latest/user_guide/modules/gradientanisotropicdiffusion.html
def process_slice(current_slice: sitk.Image) -> None:
    # show_current_slice(current_slice)
    # Image smoothing
    smooth_filter: sitk.GradientAnisotropicDiffusionImageFilter = (
        sitk.GradientAnisotropicDiffusionImageFilter()
    )
    print(smooth_filter.GetConductanceParameter())
    print(smooth_filter.GetNumberOfIterations())
    print(smooth_filter.GetTimeStep())
    smooth_filter.SetConductanceParameter(1.0)
    smooth_filter.SetNumberOfIterations(10)
    smooth_filter.SetTimeStep(0.0625)
    smooth_slice: sitk.GradientAnisotropicDiffusionImageFilter = smooth_filter.Execute(
        sitk.Cast(current_slice, sitk.sitkFloat64)
    )
    show_current_slice(smooth_slice)
    # FG/BG selection
    # TODO: user chooses between otsu and BinaryThresholdImageFilter
    # otsu = sitk.OtsuThresholdImageFilter().Execute(smooth_slice)
    # show_current_slice(otsu)
    # Fill holes
    # hole_filling = sitk.BinaryGrindPeakImageFilter().Execute(otsu)
    # show_current_slice(hole_filling)
    # # Invert image
    # inverted_image = sitk.NotImageFilter().Execute(hole_filling)
    # show_current_slice(inverted_image)
    # # Select largest component
    # largest_component = select_largest_component(inverted_image)
    # show_current_slice(largest_component)
    # # Generate contour
    # contour = sitk.BinaryContourImageFilter().Execute(largest_component)
    # show_current_slice(contour)


def show_current_slice(current_slice: sitk.Image) -> None:
    plt.imshow(sitk.GetArrayViewFromImage(current_slice))
    plt.axis("off")
    plt.show()


def show_fiji(image: sitk.Image) -> None:
    sitk.Show(sitk.Cast(image, sitk.sitkFloat32) + 255)


# Credit: https://discourse.itk.org/t/simpleitk-extract-largest-connected-component-from-binary-image/4958
def select_largest_component(binary_image: sitk.Image) -> sitk.Image:
    component_image = sitk.ConnectedComponentImageFilter().Execute(binary_image)
    sorted_component_image = sitk.RelabelComponent(
        component_image, sortByObjectSize=True
    )
    largest_component_binary_image = sorted_component_image == 1
    return largest_component_binary_image


def apply_rotations(
    image: sitk.Image, x_rotation: int, y_rotation: int, z_rotation: int
) -> sitk.Image:
    euler_transform = sitk.Euler3DTransform()
    euler_transform.SetCenter(
        image.TransformContinuousIndexToPhysicalPoint(
            [((sz - 1) / 2.0) for sz in image.GetSize()]
        )
    )
    center = image.TransformContinuousIndexToPhysicalPoint(
        [((sz - 1) / 2.0) for sz in image.GetSize()]
    )
    euler_transform.SetRotation(
        degrees_to_radians(x_rotation),
        degrees_to_radians(y_rotation),
        degrees_to_radians(z_rotation),
    )
    rotated_image = sitk.Resample(image, euler_transform)
    return rotated_image


def degrees_to_radians(num: float) -> float:
    return num * np.pi / 180


if __name__ == "__main__":
    main()

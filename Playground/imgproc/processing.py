import SimpleITK as sitk
import numpy as np
import matplotlib.pyplot as plt

OUTPUT_DIR = 'out'
NRRD1_PATH = 'ExampleData/BCP_Dataset_2month_T1w.nrrd'
NRRD2_PATH = 'ExampleData/IBIS_Dataset_12month_T1w.nrrd'
NRRD3_PATH = 'ExampleData/IBIS_Dataset_NotAligned_6month_T1w.nrrd'
NIFTI_PATH = 'ExampleData/MicroBiome_1month_T1w.nii.gz'

x_rotation = 0
y_rotation = 0
z_rotation = 0
slice_num = 89

def main() -> None:
    reader = sitk.ImageFileReader()
    reader.SetFileName(NRRD1_PATH)
    image = reader.Execute()
    # FG/BG selection
    otsu = sitk.OtsuThresholdImageFilter().Execute(image)
    # Fill holes -- maybe kind of works
    hole_filling = sitk.GrayscaleGrindPeakImageFilter().Execute(otsu)
    # Select largest component -- does not work
    largest_component = select_largest_component(hole_filling)
    show_current_slice(largest_component)

def show_current_slice(image) -> None:
    current_slice = image[:, :, slice_num]
    plt.imshow(sitk.GetArrayViewFromImage(current_slice))
    plt.axis('off')
    plt.show()

def show_fiji(image):
    sitk.Show(sitk.Cast(image,sitk.sitkFloat32) + 255)

# Does not work
# Credit: https://discourse.itk.org/t/simpleitk-extract-largest-connected-component-from-binary-image/4958
def select_largest_component(binary_image):
    component_image = sitk.ConnectedComponent(binary_image)
    sorted_component_image = sitk.RelabelComponent(component_image, sortByObjectSize=True)
    largest_component_binary_image = sorted_component_image == 1
    return largest_component_binary_image

def apply_rotations(image):
    euler_transform = sitk.Euler3DTransform(image.TransformContinuousIndexToPhysicalPoint([(sz-1 / 2.0) for sz in image.GetSize()]))
    euler_transform.SetRotation(degrees_to_radians(x_rotation), degrees_to_radians(y_rotation), degrees_to_radians(z_rotation))
    rotated_image = sitk.Resample(image, euler_transform)
    return rotated_image

def degrees_to_radians(num: float):
    return num * np.pi / 180

if __name__ == "__main__":
    main()